from __future__ import annotations

from uuid import UUID

from matrx_orm import MatrxORM

from app.db.models import Workflow
from app.db.schemas import WorkflowCreate, WorkflowResponse


async def list_workflows(db: MatrxORM) -> list[WorkflowResponse]:
    rows = await db.manager(Workflow).order_by("-created_at").all()
    return [WorkflowResponse(**row) for row in rows]


async def get_workflow(db: MatrxORM, workflow_id: UUID) -> WorkflowResponse | None:
    row = await db.manager(Workflow).get(id=str(workflow_id))
    return WorkflowResponse(**row) if row else None


async def create_workflow(db: MatrxORM, payload: WorkflowCreate) -> WorkflowResponse:
    row = await db.manager(Workflow).create(
        name=payload.name,
        description=payload.description or "",
        definition=payload.definition,
        input_schema=payload.input_schema,
    )
    return WorkflowResponse(**row)


async def update_workflow(
    db: MatrxORM, workflow_id: UUID, payload: WorkflowCreate
) -> WorkflowResponse | None:
    row = await db.manager(Workflow).update(
        id=str(workflow_id),
        name=payload.name,
        description=payload.description or "",
        definition=payload.definition,
        input_schema=payload.input_schema,
    )
    return WorkflowResponse(**row) if row else None


async def delete_workflow(db: MatrxORM, workflow_id: UUID) -> None:
    await db.manager(Workflow).delete(id=str(workflow_id))
