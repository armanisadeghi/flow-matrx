"""Event type constants for the internal event bus."""
from __future__ import annotations

RUN_STARTED = "run.started"
RUN_COMPLETED = "run.completed"
RUN_FAILED = "run.failed"
RUN_PAUSED = "run.paused"
RUN_CANCELLED = "run.cancelled"

STEP_STARTED = "step.started"
STEP_COMPLETED = "step.completed"
STEP_FAILED = "step.failed"
STEP_WAITING_APPROVAL = "step.waiting_approval"

APPROVAL_REQUIRED = "approval.required"
