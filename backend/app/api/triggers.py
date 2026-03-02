from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request, status

from app.types.schemas import RunResponse, TriggerRunRequest
from app.validation import validate_workflow

router = APIRouter()


async def _launch_engine(run_id: str) -> None:
    from app.engine.executor import WorkflowEngine

    engine = WorkflowEngine()
    await engine.execute_run(run_id)


@router.post(
    "/workflows/{workflow_id}/run", response_model=RunResponse, status_code=status.HTTP_201_CREATED
)
async def start_run_endpoint(
    workflow_id: str,
    payload: TriggerRunRequest,
    background_tasks: BackgroundTasks,
    x_idempotency_key: str | None = Header(None),
) -> RunResponse:
    from app.db.custom import wf_core

    workflow = await wf_core.get_workflow(str(workflow_id))
    if workflow.status != "published":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Only published workflows can be run"
        )
    validation = validate_workflow(
        {"nodes": workflow.definition.nodes, "edges": workflow.definition.edges}
    )
    if not validation.valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=validation.errors)

    idempotency_key = x_idempotency_key or payload.idempotency_key
    if idempotency_key:
        existing = await wf_core.get_runs({"idempotency_key": idempotency_key})
        if existing:
            return existing[0]

    run = await wf_core.create_run(
        {
            "workflow_id": str(workflow_id),
            "status": "pending",
            "trigger_type": "manual",
            "input": payload.input or {},
            "context": {},
            "idempotency_key": idempotency_key,
        }
    )

    background_tasks.add_task(_launch_engine, str(str(run.id)))
    return run


@router.post("/webhook/{workflow_id}")
async def webhook_trigger(
    workflow_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    x_idempotency_key: str | None = Header(None),
) -> dict:
    from app.db.custom import wf_core

    workflow = await wf_core.get_workflow(str(workflow_id))
    if workflow is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    validation = validate_workflow(
        {"nodes": workflow.definition.nodes, "edges": workflow.definition.edges}
    )
    if not validation.valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=validation.errors)

    body = await request.json()
    if x_idempotency_key:
        existing = await wf_core.get_runs({"idempotency_key": x_idempotency_key})
        if existing:
            return {"message": "Webhook already processed", "run_id": str(existing[0].id)}

    run = await wf_core.create_run(
        {
            "workflow_id": str(workflow_id),
            "status": "pending",
            "trigger_type": "webhook",
            "input": body,
            "context": {},
            "idempotency_key": x_idempotency_key,
        }
    )

    background_tasks.add_task(_launch_engine, str(str(run.id)))
    return {"message": "Webhook received", "run_id": str(run.id)}
