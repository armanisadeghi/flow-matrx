from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from matrx_orm import MatrxORM

from app.db.schemas import WorkflowCreate, WorkflowResponse
from app.db.queries.workflows import (
    create_workflow,
    delete_workflow,
    get_workflow,
    list_workflows,
    update_workflow,
)
from app.dependencies import get_db

router = APIRouter()


@router.get("/", response_model=list[WorkflowResponse])
async def list_workflows_endpoint(db: MatrxORM = Depends(get_db)):
    return await list_workflows(db)


@router.post("/", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow_endpoint(
    payload: WorkflowCreate, db: MatrxORM = Depends(get_db)
):
    return await create_workflow(db, payload)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow_endpoint(
    workflow_id: UUID, db: MatrxORM = Depends(get_db)
):
    workflow = await get_workflow(db, workflow_id)
    if workflow is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    return workflow


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow_endpoint(
    workflow_id: UUID, payload: WorkflowCreate, db: MatrxORM = Depends(get_db)
):
    workflow = await update_workflow(db, workflow_id, payload)
    if workflow is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    return workflow


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow_endpoint(
    workflow_id: UUID, db: MatrxORM = Depends(get_db)
):
    await delete_workflow(db, workflow_id)
