from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request, status

from app.db.schemas import RunResponse, TriggerRunRequest

router = APIRouter()


async def _launch_engine(run_id: UUID) -> None:
    from app.engine.executor import WorkflowEngine

    engine = WorkflowEngine()
    await engine.execute_run(run_id)


@router.post("/workflows/{workflow_id}/run", response_model=RunResponse, status_code=status.HTTP_201_CREATED)
async def start_run_endpoint(
    workflow_id: UUID,
    payload: TriggerRunRequest,
    background_tasks: BackgroundTasks,
    x_idempotency_key: str | None = Header(None),
) -> RunResponse:
    from app.db.models import (
        run_manager_instance as run_mgr,
        workflow_manager_instance as wf_mgr,
    )

    workflow = await wf_mgr.load_by_id(str(workflow_id))
    if workflow is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    if workflow.status != "published":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only published workflows can be run")

    idempotency_key = x_idempotency_key or payload.idempotency_key
    if idempotency_key:
        existing = await run_mgr.filter_items(idempotency_key=idempotency_key)
        if existing:
            return RunResponse(**existing[0].__dict__)

    run = await run_mgr.create_item(
        workflow_id=str(workflow_id),
        status="pending",
        trigger_type="manual",
        input=payload.input or {},
        context={},
        idempotency_key=idempotency_key,
    )

    background_tasks.add_task(_launch_engine, UUID(str(run.id)))
    return RunResponse(**run.__dict__)


@router.post("/webhook/{workflow_id}")
async def webhook_trigger(
    workflow_id: UUID,
    request: Request,
    background_tasks: BackgroundTasks,
    x_idempotency_key: str | None = Header(None),
) -> dict:
    from app.db.models import (
        run_manager_instance as run_mgr,
        workflow_manager_instance as wf_mgr,
    )

    workflow = await wf_mgr.load_by_id(str(workflow_id))
    if workflow is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    if workflow.status != "published":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only published workflows can be triggered")

    body = await request.json()
    if x_idempotency_key:
        existing = await run_mgr.filter_items(idempotency_key=x_idempotency_key)
        if existing:
            return {"message": "Webhook already processed", "run_id": str(existing[0].id)}

    run = await run_mgr.create_item(
        workflow_id=str(workflow_id),
        status="pending",
        trigger_type="webhook",
        input=body,
        context={},
        idempotency_key=x_idempotency_key,
    )

    background_tasks.add_task(_launch_engine, UUID(str(run.id)))
    return {"message": "Webhook received", "run_id": str(run.id)}
