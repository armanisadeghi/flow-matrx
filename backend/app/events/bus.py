"""In-process event bus for broadcasting run events to WebSocket subscribers."""
from __future__ import annotations

import asyncio
from typing import Any


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[asyncio.Queue]] = {}

    def subscribe(self, run_id: str, queue: asyncio.Queue) -> None:
        self._subscribers.setdefault(run_id, []).append(queue)

    def unsubscribe(self, run_id: str, queue: asyncio.Queue) -> None:
        subscribers = self._subscribers.get(run_id, [])
        if queue in subscribers:
            subscribers.remove(queue)

    async def emit(self, event_type: str, **kwargs: Any) -> None:
        run_id = str(kwargs.get("run_id", ""))
        event: dict[str, Any] = {"type": event_type}
        for k, v in kwargs.items():
            # Preserve dicts/lists as-is; convert everything else to string.
            event[k] = v if isinstance(v, (dict, list, bool, int, float, type(None))) else str(v)
        for queue in self._subscribers.get(run_id, []):
            await queue.put(event)


event_bus = EventBus()
