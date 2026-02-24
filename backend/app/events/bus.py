from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

import structlog

from app.events.types import EventType

logger = structlog.get_logger(__name__)


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[asyncio.Queue[dict[str, Any]]]] = {}

    def subscribe(self, run_id: str, queue: asyncio.Queue[dict[str, Any]]) -> None:
        self._subscribers.setdefault(run_id, []).append(queue)

    def unsubscribe(self, run_id: str, queue: asyncio.Queue[dict[str, Any]]) -> None:
        subscribers = self._subscribers.get(run_id, [])
        if queue in subscribers:
            subscribers.remove(queue)
        if not subscribers:
            self._subscribers.pop(run_id, None)

    async def emit(
        self,
        run_id: UUID | str,
        event_type: EventType | str,
        step_id: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> None:
        run_id_str = str(run_id)
        payload = payload or {}

        event: dict[str, Any] = {
            "type": str(event_type),
            "run_id": run_id_str,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if step_id is not None:
            event["step_id"] = step_id
        event["payload"] = payload

        await self._persist(run_id_str, event_type, step_id, payload)

        for queue in self._subscribers.get(run_id_str, []):
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                logger.warning("Subscriber queue full, dropping event", run_id=run_id_str)

    async def _persist(
        self,
        run_id: str,
        event_type: EventType | str,
        step_id: str | None,
        payload: dict[str, Any],
    ) -> None:
        try:
            from app.db.models import run_event_manager_instance as mgr

            await mgr.create_item(
                run_id=run_id,
                step_id=step_id,
                event_type=str(event_type),
                payload=payload,
            )
        except Exception:
            logger.exception("Failed to persist event to run_events", run_id=run_id)


event_bus = EventBus()
