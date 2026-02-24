from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from app.db.schemas import (
    ResumeRunRequest,
    RunEventResponse,
    RunResponse,
    StepRunResponse,
)

router = APIRouter()


async def _launch_engine(run_id: UUID) -> None:
    from app.engine.executor import WorkflowEngine

    engine = WorkflowEngine()
    await engine.execute_run(run_id)


@router.get("/", response_model=list[RunResponse])
async def list_runs_endpoint(
    workflow_id: UUID | None = None,
    run_status: str | None = None,
) -> list[RunResponse]:
    from app.db.models import run_manager_instance as mgr

    filters: dict[str, str] = {}
    if workflow_id:
        filters["workflow_id"] = str(workflow_id)
    if run_status:
        filters["status"] = run_status

    items = await mgr.filter_items(**filters) if filters else await mgr.load_items()
    return [RunResponse(**item.__dict__) for item in items]


@router.get("/{run_id}", response_model=RunResponse)
async def get_run_endpoint(run_id: UUID) -> RunResponse:
    from app.db.models import run_manager_instance as mgr

    item = await mgr.load_by_id(str(run_id))
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return RunResponse(**item.__dict__)


@router.get("/{run_id}/steps", response_model=list[StepRunResponse])
async def get_run_steps_endpoint(run_id: UUID) -> list[StepRunResponse]:
    from app.db.models import step_run_manager_instance as mgr

    items = await mgr.filter_items(run_id=str(run_id))
    return [StepRunResponse(**item.__dict__) for item in items]


@router.get("/{run_id}/events", response_model=list[RunEventResponse])
async def get_run_events_endpoint(run_id: UUID) -> list[RunEventResponse]:
    from app.db.models import run_event_manager_instance as mgr

    items = await mgr.filter_items(run_id=str(run_id))
    return [RunEventResponse(**item.__dict__) for item in items]


@router.post("/{run_id}/cancel", status_code=status.HTTP_202_ACCEPTED)
async def cancel_run_endpoint(run_id: UUID) -> dict[str, str]:
    from app.db.models import run_manager_instance as mgr

    run = await mgr.load_by_id(str(run_id))
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    if run.status not in ("running", "paused", "pending"):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Cannot cancel run in state: {run.status}")
    await mgr.update_item(str(run_id), status="cancelled")
    return {"message": "Cancellation requested", "run_id": str(run_id)}


@router.post("/{run_id}/resume", status_code=status.HTTP_202_ACCEPTED)
async def resume_run_endpoint(
    run_id: UUID, payload: ResumeRunRequest, background_tasks: BackgroundTasks,
) -> dict[str, str]:
    from app.db.models import (
        run_manager_instance as run_mgr,
        step_run_manager_instance as sr_mgr,
    )
    from app.events.bus import event_bus
    from app.events.types import EventType

    run = await run_mgr.load_by_id(str(run_id))
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    if run.status != "paused":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Run is not paused, current state: {run.status}")

    await sr_mgr.update_item(
        None,
        _filter={"run_id": str(run_id), "step_id": payload.step_id, "status": "waiting"},
        status="completed",
        output=payload.approval_data or {},
        completed_at="now()",
    )

    await run_mgr.update_item(str(run_id), status="running")
    await event_bus.emit(
        run_id, EventType.RUN_RESUMED,
        payload={"status": "running", "resumed_step_id": payload.step_id},
    )

    background_tasks.add_task(_launch_engine, run_id)
    return {"message": "Resume requested", "run_id": str(run_id)}


@router.post("/{run_id}/retry", status_code=status.HTTP_202_ACCEPTED)
async def retry_run_endpoint(run_id: UUID, background_tasks: BackgroundTasks) -> dict[str, str]:
    from app.db.models import (
        run_manager_instance as run_mgr,
        step_run_manager_instance as sr_mgr,
    )

    run = await run_mgr.load_by_id(str(run_id))
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    if run.status != "failed":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only failed runs can be retried")

    failed_steps = await sr_mgr.filter_items(run_id=str(run_id), status="failed")
    for step in failed_steps:
        await sr_mgr.update_item(
            None,
            _filter={"run_id": str(run_id), "step_id": step.step_id, "attempt": step.attempt},
            status="pending",
            error=None,
            completed_at=None,
        )

    await run_mgr.update_item(str(run_id), status="pending")
    background_tasks.add_task(_launch_engine, run_id)
    return {"message": "Retry requested", "run_id": str(run_id)}
