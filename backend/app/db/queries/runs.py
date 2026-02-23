from __future__ import annotations

from uuid import UUID

from matrx_orm import MatrxORM

from app.db.models import Run
from app.db.schemas import RunResponse


async def list_runs_for_workflow(db: MatrxORM, workflow_id: UUID) -> list[RunResponse]:
    rows = await db.manager(Run).filter(
        workflow_id=str(workflow_id)
    ).order_by("-started_at").all()
    return [RunResponse(**row) for row in rows]


async def get_run(db: MatrxORM, run_id: UUID) -> RunResponse | None:
    row = await db.manager(Run).get(id=str(run_id))
    return RunResponse(**row) if row else None
