from __future__ import annotations

from uuid import UUID

from app.db.models import run_manager_instance as mgr
from app.db.schemas import RunResponse


async def list_runs(workflow_id: UUID | None = None, run_status: str | None = None) -> list[RunResponse]:
    filters: dict = {}
    if workflow_id:
        filters["workflow_id"] = str(workflow_id)
    if run_status:
        filters["status"] = run_status

    items = await mgr.filter_items(**filters) if filters else await mgr.load_items()
    return [RunResponse(**item.__dict__) for item in items]


async def get_run(run_id: UUID) -> RunResponse | None:
    item = await mgr.load_by_id(str(run_id))
    return RunResponse(**item.__dict__) if item else None
