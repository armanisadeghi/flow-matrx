from __future__ import annotations


class EngineError(Exception):
    pass


class PauseExecution(EngineError):
    def __init__(self, step_id: str, reason: str = "") -> None:
        self.step_id = step_id
        self.reason = reason
        super().__init__(f"Execution paused at step {step_id!r}: {reason}")


class StepTimeout(EngineError):
    def __init__(self, step_id: str, timeout_seconds: float) -> None:
        self.step_id = step_id
        self.timeout_seconds = timeout_seconds
        super().__init__(f"Step {step_id!r} timed out after {timeout_seconds}s")


class WorkflowValidationError(EngineError):
    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__(f"Workflow validation failed: {'; '.join(errors)}")
