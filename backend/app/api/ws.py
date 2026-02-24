from __future__ import annotations

import asyncio
from uuid import UUID

import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.events.bus import event_bus

logger = structlog.get_logger(__name__)
router = APIRouter()


async def _build_snapshot(run_id: str) -> dict:
    from app.db.models import (
        run_manager_instance as run_mgr,
        step_run_manager_instance as sr_mgr,
    )

    run = await run_mgr.load_by_id(run_id)
    if run is None:
        return {"type": "snapshot", "run_id": run_id, "error": "Run not found"}

    step_runs = await sr_mgr.filter_items(run_id=run_id)
    steps_data = [
        {
            "step_id": sr.step_id,
            "step_type": sr.step_type,
            "status": sr.status,
            "attempt": sr.attempt,
            "error": sr.error,
        }
        for sr in step_runs
    ]

    return {
        "type": "snapshot",
        "run_id": run_id,
        "run_status": run.status,
        "context": run.context or {},
        "steps": steps_data,
    }


@router.websocket("/ws/runs/{run_id}")
async def run_websocket(websocket: WebSocket, run_id: UUID) -> None:
    await websocket.accept()
    run_id_str = str(run_id)
    queue: asyncio.Queue[dict] = asyncio.Queue(maxsize=256)
    event_bus.subscribe(run_id_str, queue)

    try:
        # Subscribe before snapshot to avoid dropping events during connect.
        snapshot = await _build_snapshot(run_id_str)
        await websocket.send_json(snapshot)

        while True:
            event = await queue.get()
            await websocket.send_json(event)
    except WebSocketDisconnect:
        pass
    except Exception:
        logger.exception("WebSocket error", run_id=run_id_str)
    finally:
        event_bus.unsubscribe(run_id_str, queue)
