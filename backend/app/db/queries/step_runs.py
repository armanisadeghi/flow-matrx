from __future__ import annotations

from uuid import UUID

from app.db.models import step_run_manager_instance as mgr
from app.db.schemas import StepRunResponse


async def get_step_runs_for_run(run_id: UUID) -> list[StepRunResponse]:
    items = await mgr.filter_items(run_id=str(run_id))
    return [StepRunResponse(**item.__dict__) for item in items]
