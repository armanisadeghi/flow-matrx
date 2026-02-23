from __future__ import annotations

from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, Request

from app.dependencies import get_db

router = APIRouter()


@router.post("/webhook/{workflow_id}")
async def webhook_trigger(
    workflow_id: UUID,
    request: Request,
    db: asyncpg.Connection = Depends(get_db),
):
    payload = await request.json()
    # TODO: validate secret, enqueue run
    return {"message": "Webhook received", "workflow_id": str(workflow_id)}
