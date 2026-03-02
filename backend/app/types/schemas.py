from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

# -- Workflow schemas ----------------------------------------------------------

class WorkflowCreate(BaseModel):
    name: str
    description: str | None = None
    definition: dict[str, Any] = Field(default_factory=lambda: {"nodes": [], "edges": []})
    input_schema: dict[str, Any] | None = None


class WorkflowUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    definition: dict[str, Any] | None = None
    input_schema: dict[str, Any] | None = None


class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: str = ""
    version: int
    status: str
    definition: dict[str, Any]
    input_schema: dict[str, Any] | None = None
    user_id: str
    created_at: datetime
    updated_at: datetime


# -- Run schemas ---------------------------------------------------------------

class TriggerRunRequest(BaseModel):
    input: dict[str, Any] | None = None
    idempotency_key: str | None = None


class RunResponse(BaseModel):
    id: str
    org_id: str
    user_id: str
    workflow_id: str
    status: str
    trigger_type: str
    input: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    idempotency_key: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime


class ResumeRunRequest(BaseModel):
    step_id: str
    approval_data: dict[str, Any] | None = None


# -- StepRun schemas -----------------------------------------------------------

class StepRunResponse(BaseModel):
    id: str
    org_id: str
    user_id: str
    run_id: str
    step_id: str
    step_type: str
    status: str
    input: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    attempt: int
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime


# -- RunEvent schemas ----------------------------------------------------------

class RunEventResponse(BaseModel):
    id: str
    org_id: str
    user_id: str
    run_id: str
    step_id: str | None = None
    event_type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


# -- Validation ----------------------------------------------------------------

class ValidationResult(BaseModel):
    valid: bool
    errors: list[str]


# -- Catalog -------------------------------------------------------------------

class StepTypeInfo(BaseModel):
    type: str
    label: str
    icon: str
    category: str
    description: str
    config_schema: dict[str, Any] = Field(default_factory=dict)
