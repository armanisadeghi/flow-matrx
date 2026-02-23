from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel


class WorkflowCreate(BaseModel):
    name: str
    description: str | None = None
    definition: dict[str, Any]


class WorkflowResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    definition: dict[str, Any]
    created_at: str
    updated_at: str


class TriggerRunRequest(BaseModel):
    trigger_payload: dict[str, Any] | None = None


class RunResponse(BaseModel):
    id: UUID
    workflow_id: UUID
    status: str
    trigger_payload: dict[str, Any] | None = None
    started_at: str
    completed_at: str | None = None
    error_message: str | None = None
