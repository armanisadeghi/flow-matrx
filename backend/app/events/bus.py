from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from datetime import datetime, timezone
from typing import Any, Protocol
from uuid import UUID

import structlog

from app.events.types import EventType

logger = structlog.get_logger(__name__)


class EventPersister(Protocol):
    """Protocol for event persistence backends.  Inject a mock for tests."""

    async def insert_run_event(
        self,
        run_id: str,
        event_type: str,
        step_id: str | None,
        payload: dict[str, Any],
    ) -> None: ...


class _DefaultPersister:
    """Persists events via the ORM.  Imported lazily to avoid circular deps."""

    async def insert_run_event(
        self,
        run_id: str,
        event_type: str,
        step_id: str | None,
        payload: dict[str, Any],
    ) -> None:
        from app.db.models import run_event_manager_instance as mgr

        await mgr.create_item(
            run_id=run_id,
            step_id=step_id,
            event_type=event_type,
            payload=payload,
        )


class EventBus:
    def __init__(self, persister: EventPersister | None = None) -> None:
        self._persister: EventPersister = persister or _DefaultPersister()
        self._subscribers: dict[str, list[asyncio.Queue[dict[str, Any]]]] = {}
        self._listeners: list[
            Callable[[dict[str, Any]], Coroutine[Any, Any, None]]
        ] = []

    # -- subscription ----------------------------------------------------------

    def subscribe(
        self, run_id: str, queue: asyncio.Queue[dict[str, Any]] | None = None
    ) -> asyncio.Queue[dict[str, Any]]:
        """Subscribe to events for a run.  Returns the queue (creates one if None)."""
        if queue is None:
            queue = asyncio.Queue(maxsize=256)
        self._subscribers.setdefault(run_id, []).append(queue)
        return queue

    def unsubscribe(self, run_id: str, queue: asyncio.Queue[dict[str, Any]]) -> None:
        subscribers = self._subscribers.get(run_id, [])
        if queue in subscribers:
            subscribers.remove(queue)
        if not subscribers:
            self._subscribers.pop(run_id, None)

    def add_listener(
        self, callback: Callable[[dict[str, Any]], Coroutine[Any, Any, None]]
    ) -> None:
        """Register a global listener called on every event (useful for metrics)."""
        self._listeners.append(callback)

    def remove_listener(
        self, callback: Callable[[dict[str, Any]], Coroutine[Any, Any, None]]
    ) -> None:
        self._listeners = [cb for cb in self._listeners if cb is not callback]

    # -- emit ------------------------------------------------------------------

    async def emit(
        self,
        run_id: UUID | str,
        event_type: EventType | str,
        step_id: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        run_id_str = str(run_id)
        event_type_str = str(event_type)
        payload = payload or {}

        event: dict[str, Any] = {
            "type": event_type_str,
            "event_type": event_type_str,
            "run_id": run_id_str,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if step_id is not None:
            event["step_id"] = step_id
        event["payload"] = payload

        # Persist to DB
        try:
            await self._persister.insert_run_event(
                run_id=run_id_str,
                event_type=event_type_str,
                step_id=step_id,
                payload=payload,
            )
        except Exception:
            logger.exception("Failed to persist event", run_id=run_id_str)

        # Fan-out to per-run subscribers
        for queue in self._subscribers.get(run_id_str, []):
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                logger.warning(
                    "Subscriber queue full, dropping event", run_id=run_id_str
                )

        # Fan-out to global listeners
        for listener in self._listeners:
            try:
                await listener(event)
            except Exception:
                logger.exception("Listener error", run_id=run_id_str)

        return event


event_bus = EventBus()
