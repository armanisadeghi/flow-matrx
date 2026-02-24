from __future__ import annotations

from uuid import UUID

from app.db.models import workflow_manager_instance as mgr
from app.db.schemas import WorkflowCreate, WorkflowResponse, WorkflowUpdate


async def list_workflows() -> list[WorkflowResponse]:
    items = await mgr.load_items()
    return [WorkflowResponse(**item.__dict__) for item in items]


async def get_workflow(workflow_id: UUID) -> WorkflowResponse | None:
    item = await mgr.load_by_id(str(workflow_id))
    return WorkflowResponse(**item.__dict__) if item else None


async def create_workflow(payload: WorkflowCreate) -> WorkflowResponse:
    item = await mgr.create_item(
        name=payload.name,
        description=payload.description or "",
        definition=payload.definition,
        input_schema=payload.input_schema,
    )
    return WorkflowResponse(**item.__dict__)


async def update_workflow(workflow_id: UUID, payload: WorkflowUpdate) -> WorkflowResponse | None:
    update_data: dict = {}
    if payload.name is not None:
        update_data["name"] = payload.name
    if payload.description is not None:
        update_data["description"] = payload.description
    if payload.definition is not None:
        update_data["definition"] = payload.definition
    if payload.input_schema is not None:
        update_data["input_schema"] = payload.input_schema

    if not update_data:
        return await get_workflow(workflow_id)

    item = await mgr.update_item(str(workflow_id), **update_data)
    return WorkflowResponse(**item.__dict__) if item else None


async def delete_workflow(workflow_id: UUID) -> None:
    await mgr.delete_item(str(workflow_id))
