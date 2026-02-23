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
        event = {"type": event_type, **{k: str(v) for k, v in kwargs.items()}}
        for queue in self._subscribers.get(run_id, []):
            await queue.put(event)


event_bus = EventBus()
