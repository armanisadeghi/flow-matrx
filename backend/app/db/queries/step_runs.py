from __future__ import annotations

from uuid import UUID

from matrx_orm import MatrxORM

from app.db.models import StepRun


async def get_step_runs_for_run(db: MatrxORM, run_id: UUID) -> list[dict]:
    rows = await db.manager(StepRun).filter(run_id=str(run_id)).all()
    return list(rows)
