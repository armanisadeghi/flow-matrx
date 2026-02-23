from __future__ import annotations

from typing import Any
from uuid import UUID

import asyncpg

from app.db.models import WorkflowCreate, WorkflowResponse


async def list_workflows(conn: asyncpg.Connection) -> list[WorkflowResponse]:
    rows = await conn.fetch("SELECT * FROM workflows ORDER BY created_at DESC")
    return [WorkflowResponse(**dict(row)) for row in rows]


async def get_workflow(conn: asyncpg.Connection, workflow_id: UUID) -> WorkflowResponse | None:
    row = await conn.fetchrow("SELECT * FROM workflows WHERE id = $1", workflow_id)
    return WorkflowResponse(**dict(row)) if row else None


async def create_workflow(
    conn: asyncpg.Connection, payload: WorkflowCreate
) -> WorkflowResponse:
    row = await conn.fetchrow(
        """
        INSERT INTO workflows (name, description, definition)
        VALUES ($1, $2, $3)
        RETURNING *
        """,
        payload.name,
        payload.description,
        payload.definition,
    )
    return WorkflowResponse(**dict(row))


async def update_workflow(
    conn: asyncpg.Connection, workflow_id: UUID, payload: WorkflowCreate
) -> WorkflowResponse | None:
    row = await conn.fetchrow(
        """
        UPDATE workflows SET name=$1, description=$2, definition=$3, updated_at=now()
        WHERE id=$4 RETURNING *
        """,
        payload.name,
        payload.description,
        payload.definition,
        workflow_id,
    )
    return WorkflowResponse(**dict(row)) if row else None


async def delete_workflow(conn: asyncpg.Connection, workflow_id: UUID) -> None:
    await conn.execute("DELETE FROM workflows WHERE id = $1", workflow_id)
