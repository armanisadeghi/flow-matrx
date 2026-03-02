from __future__ import annotations

import asyncio

import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.events.bus import event_bus

logger = structlog.get_logger(__name__)
router = APIRouter()


async def _build_snapshot(run_id: str) -> dict:
    from app.db.custom import wf_core

    run = await wf_core.get_run(run_id)
    if not run:
        return {"type": "snapshot", "run_id": run_id, "error": "Run not found"}

    step_runs = await wf_core.get_step_runs({"run_id": run_id})
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
async def run_websocket(websocket: WebSocket, run_id: str) -> None:
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
