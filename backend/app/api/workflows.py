from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status

from app.db.schemas import (
    ValidationResult,
    WorkflowCreate,
    WorkflowResponse,
    WorkflowUpdate,
)
from app.db.queries.workflows import (
    create_workflow,
    delete_workflow,
    get_workflow,
    list_workflows,
    update_workflow,
)
from app.validation.workflow import validate_workflow

router = APIRouter()


@router.get("/", response_model=list[WorkflowResponse])
async def list_workflows_endpoint() -> list[WorkflowResponse]:
    return await list_workflows()


@router.post("/", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow_endpoint(
    payload: WorkflowCreate,
    x_idempotency_key: str | None = Header(None),
) -> WorkflowResponse:
    return await create_workflow(payload)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow_endpoint(workflow_id: UUID) -> WorkflowResponse:
    wf = await get_workflow(workflow_id)
    if wf is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    return wf


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow_endpoint(workflow_id: UUID, payload: WorkflowUpdate) -> WorkflowResponse:
    existing = await get_workflow(workflow_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    if existing.status == "published":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Published workflows are immutable. Duplicate to create a new draft.",
        )
    result = await update_workflow(workflow_id, payload)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    return result


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow_endpoint(workflow_id: UUID) -> None:
    existing = await get_workflow(workflow_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    if existing.status == "published":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot delete published workflows")
    await delete_workflow(workflow_id)


@router.post("/{workflow_id}/publish", response_model=WorkflowResponse)
async def publish_workflow_endpoint(workflow_id: UUID) -> WorkflowResponse:
    from app.db.models import workflow_manager_instance as wf_mgr

    existing = await get_workflow(workflow_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

    errors = validate_workflow(existing.definition)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Workflow validation failed", "errors": errors},
        )

    await wf_mgr.update_item(str(workflow_id), status="published")
    result = await get_workflow(workflow_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found after publish")
    return result


@router.post("/{workflow_id}/validate", response_model=ValidationResult)
async def validate_workflow_endpoint(workflow_id: UUID) -> ValidationResult:
    existing = await get_workflow(workflow_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    errors = validate_workflow(existing.definition)
    return ValidationResult(valid=len(errors) == 0, errors=errors)


@router.post("/{workflow_id}/duplicate", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_workflow_endpoint(workflow_id: UUID) -> WorkflowResponse:
    existing = await get_workflow(workflow_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    payload = WorkflowCreate(
        name=f"{existing.name} (copy)",
        description=existing.description,
        definition=existing.definition,
        input_schema=existing.input_schema,
    )
    return await create_workflow(payload)
