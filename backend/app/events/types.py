from __future__ import annotations

from enum import StrEnum


class EventType(StrEnum):
    RUN_STARTED = "run.started"
    RUN_COMPLETED = "run.completed"
    RUN_FAILED = "run.failed"
    RUN_PAUSED = "run.paused"
    RUN_RESUMED = "run.resumed"
    RUN_CANCELLED = "run.cancelled"

    STEP_STARTED = "step.started"
    STEP_COMPLETED = "step.completed"
    STEP_FAILED = "step.failed"
    STEP_SKIPPED = "step.skipped"
    STEP_WAITING = "step.waiting"
    STEP_RETRYING = "step.retrying"

    CONTEXT_UPDATED = "context.updated"
