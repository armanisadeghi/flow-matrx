from __future__ import annotations

from dataclasses import asdict, is_dataclass

from fastapi import APIRouter, Header, HTTPException, status

from app.db.custom import wf_core
from app.types.schemas import ValidationResult, WorkflowCreate, WorkflowResponse, WorkflowUpdate
from app.validation import validate_workflow

router = APIRouter()


def _definition_to_dict(definition: object) -> dict:
    """Convert a WfWorkflowDefinition dataclass (or plain dict) to a plain dict."""
    if is_dataclass(definition) and not isinstance(definition, type):
        return asdict(definition)  # type: ignore[arg-type]
    if isinstance(definition, dict):
        return definition
    return {}


@router.get("/", response_model=list[WorkflowResponse])
async def list_workflows_endpoint() -> list[WorkflowResponse]:
    user_id = "this-will-come-from-context-later"
    return await wf_core.get_workflow_responses({"created_by": user_id})


@router.post("/", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow_endpoint(
    payload: WorkflowCreate,
    x_idempotency_key: str | None = Header(None),
) -> WorkflowResponse:
    return await wf_core.create_workflow(**payload.model_dump(exclude_none=False))


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow_endpoint(workflow_id: str) -> WorkflowResponse:
    wf = await wf_core.get_workflow_response(str(workflow_id))
    if not wf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    return wf


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow_endpoint(workflow_id: str, payload: WorkflowUpdate) -> WorkflowResponse:
    existing = await wf_core.get_workflow(str(workflow_id))
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    if existing.status == "published":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Published workflows are immutable. Duplicate to create a new draft.",
        )
    return await wf_core.update_workflow(str(workflow_id), **payload.model_dump(exclude_none=True))


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow_endpoint(workflow_id: str) -> None:
    existing = await wf_core.get_workflow(str(workflow_id))
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    if existing.status == "published":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Cannot delete published workflows"
        )
    await wf_core.delete_workflow(str(workflow_id))


@router.post("/{workflow_id}/publish", response_model=WorkflowResponse)
async def publish_workflow_endpoint(workflow_id: str) -> WorkflowResponse:
    existing = await wf_core.get_workflow(str(workflow_id))
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

    definition_dict = _definition_to_dict(existing.definition)
    validation = validate_workflow(definition_dict)
    if not validation.valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Workflow validation failed", "errors": validation.errors},
        )

    await wf_core.update_workflow(str(workflow_id), status="published")
    result = await wf_core.get_workflow_response(str(workflow_id))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found after publish"
        )
    return result


@router.post("/{workflow_id}/validate", response_model=ValidationResult)
async def validate_workflow_endpoint(workflow_id: str) -> ValidationResult:
    existing = await wf_core.get_workflow(str(workflow_id))
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    definition_dict = _definition_to_dict(existing.definition)
    return validate_workflow(definition_dict)


@router.post(
    "/{workflow_id}/duplicate", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED
)
async def duplicate_workflow_endpoint(workflow_id: str) -> WorkflowResponse:
    existing = await wf_core.get_workflow(str(workflow_id))
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    definition_dict = _definition_to_dict(existing.definition)
    input_schema_dict = (
        asdict(existing.input_schema)
        if is_dataclass(existing.input_schema) and not isinstance(existing.input_schema, type)
        else existing.input_schema
    )
    return await wf_core.create_workflow(
        name=f"{existing.name} (copy)",
        description=existing.description,
        definition=definition_dict,
        input_schema=input_schema_dict,
    )
