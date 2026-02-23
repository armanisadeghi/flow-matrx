from __future__ import annotations

from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status

from app.db.models import RunResponse, TriggerRunRequest
from app.db.queries.runs import get_run, list_runs_for_workflow
from app.dependencies import get_db

router = APIRouter()


@router.get("/workflow/{workflow_id}", response_model=list[RunResponse])
async def list_runs_endpoint(
    workflow_id: UUID, db: asyncpg.Connection = Depends(get_db)
):
    return await list_runs_for_workflow(db, workflow_id)


@router.get("/{run_id}", response_model=RunResponse)
async def get_run_endpoint(run_id: UUID, db: asyncpg.Connection = Depends(get_db)):
    run = await get_run(db, run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return run


@router.post("/workflow/{workflow_id}/trigger", status_code=status.HTTP_202_ACCEPTED)
async def trigger_run_endpoint(
    workflow_id: UUID,
    payload: TriggerRunRequest,
    db: asyncpg.Connection = Depends(get_db),
):
    # TODO: enqueue run via arq worker
    return {"message": "Run enqueued", "workflow_id": str(workflow_id)}


@router.post("/{run_id}/cancel", status_code=status.HTTP_202_ACCEPTED)
async def cancel_run_endpoint(run_id: UUID, db: asyncpg.Connection = Depends(get_db)):
    return {"message": "Cancellation requested", "run_id": str(run_id)}


@router.post("/{run_id}/resume", status_code=status.HTTP_202_ACCEPTED)
async def resume_run_endpoint(run_id: UUID, db: asyncpg.Connection = Depends(get_db)):
    return {"message": "Resume requested", "run_id": str(run_id)}
