from __future__ import annotations

import asyncio
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.events.bus import event_bus

router = APIRouter()


@router.websocket("/ws/runs/{run_id}")
async def run_websocket(websocket: WebSocket, run_id: UUID):
    await websocket.accept()
    queue: asyncio.Queue = asyncio.Queue()
    event_bus.subscribe(str(run_id), queue)
    try:
        while True:
            event = await queue.get()
            await websocket.send_json(event)
    except WebSocketDisconnect:
        event_bus.unsubscribe(str(run_id), queue)
