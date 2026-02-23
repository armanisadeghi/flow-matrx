from __future__ import annotations

from uuid import UUID

import asyncpg


async def get_step_runs_for_run(conn: asyncpg.Connection, run_id: UUID) -> list[dict]:
    rows = await conn.fetch("SELECT * FROM step_runs WHERE run_id=$1", run_id)
    return [dict(row) for row in rows]
