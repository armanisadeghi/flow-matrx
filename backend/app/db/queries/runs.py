from __future__ import annotations

from uuid import UUID

import asyncpg

from app.db.models import RunResponse


async def list_runs_for_workflow(
    conn: asyncpg.Connection, workflow_id: UUID
) -> list[RunResponse]:
    rows = await conn.fetch(
        "SELECT * FROM runs WHERE workflow_id=$1 ORDER BY started_at DESC", workflow_id
    )
    return [RunResponse(**dict(row)) for row in rows]


async def get_run(conn: asyncpg.Connection, run_id: UUID) -> RunResponse | None:
    row = await conn.fetchrow("SELECT * FROM runs WHERE id=$1", run_id)
    return RunResponse(**dict(row)) if row else None
