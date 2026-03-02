from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from app.db.custom import wf_core
from app.events.types import EventType
from app.types.schemas import ResumeRunRequest, RunEventResponse, RunResponse, StepRunResponse

router = APIRouter()


async def _launch_engine(run_id: str) -> None:
    from app.engine.executor import WorkflowEngine

    engine = WorkflowEngine()
    await engine.execute_run(run_id)


@router.get("/", response_model=list[RunResponse])
async def list_runs_endpoint(
    workflow_id: str | None = None,
    run_status: str | None = None,
) -> list[RunResponse]:

    filters: dict[str, str] = {}
    if workflow_id:
        filters["workflow_id"] = str(workflow_id)
    if run_status:
        filters["status"] = run_status

    items = await wf_core.get_runs(filters)
    return items


@router.get("/{run_id}", response_model=RunResponse)
async def get_run_endpoint(run_id: str) -> RunResponse:

    item = await wf_core.get_run(str(run_id))
    return item


@router.get("/{run_id}/steps", response_model=list[StepRunResponse])
async def get_run_steps_endpoint(run_id: str) -> list[StepRunResponse]:

    items = await wf_core.get_step_runs_for_run(str(run_id))
    return items


@router.get("/{run_id}/events", response_model=list[RunEventResponse])
async def get_run_events_endpoint(run_id: str) -> list[RunEventResponse]:

    items = await wf_core.get_run_events({"run_id": str(run_id)})
    return items


@router.post("/{run_id}/cancel", status_code=status.HTTP_202_ACCEPTED)
async def cancel_run_endpoint(run_id: str) -> dict[str, str]:

    if await wf_core.update_run(str(run_id), {"status": "cancelled"}):
        return {"message": "Cancellation requested", "run_id": str(run_id)}
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT, detail="Cannot cancel run in current state"
    )


@router.post("/{run_id}/resume", status_code=status.HTTP_202_ACCEPTED)
async def resume_run_endpoint(
    run_id: str,
    payload: ResumeRunRequest,
    background_tasks: BackgroundTasks,
) -> dict[str, str]:

    run = await wf_core.get_run(str(run_id))
    if run.status != "paused":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Run is not paused, current state: {run.status}",
        )
    await wf_core.update_run(str(run_id), {"status": "running"})
    await wf_core.create_run_event(
        str(run_id),
        EventType.RUN_RESUMED,
        payload.step_id,
        {"status": "running", "resumed_step_id": payload.step_id},
    )

    background_tasks.add_task(_launch_engine, run_id)
    return {"message": "Resume requested", "run_id": str(run_id)}


@router.post("/{run_id}/retry", status_code=status.HTTP_202_ACCEPTED)
async def retry_run_endpoint(run_id: str, background_tasks: BackgroundTasks) -> dict[str, str]:

    run = await wf_core.get_run(str(run_id))
    if run.status != "failed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Only failed runs can be retried"
        )

    failed_steps = await wf_core.get_step_runs_for_run(str(run_id))
    for step in failed_steps:
        if step.status == "failed":
            await wf_core.update_step_run(step.id, {"status": "pending"})

    await wf_core.update_run(str(run_id), {"status": "pending"})
    background_tasks.add_task(_launch_engine, run_id)
    return {"message": "Retry requested", "run_id": str(run_id)}
