from __future__ import annotations


class EngineError(Exception):
    pass


class PauseExecution(EngineError):
    """Raised by steps that need to pause the run (approval, external event, etc.)."""

    def __init__(self, step_id: str, reason: str = "", pause_type: str = "approval") -> None:
        self.step_id = step_id
        self.reason = reason
        self.pause_type = pause_type  # "approval" | "event" | "manual"
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


class RetriableError(EngineError):
    """Explicitly marks an error as safe to retry."""

    def __init__(self, message: str, original: Exception | None = None) -> None:
        self.original = original
        super().__init__(message)


class NonRetriableError(EngineError):
    """Explicitly marks an error as non-retriable — fail immediately."""

    def __init__(self, message: str, original: Exception | None = None) -> None:
        self.original = original
        super().__init__(message)


class RunCancelled(EngineError):
    """Raised internally when a run is cancelled mid-execution."""
    pass


class RunTimeout(EngineError):
    """Raised when a run exceeds its maximum allowed duration."""

    def __init__(self, run_id: str, timeout_seconds: float) -> None:
        self.run_id = run_id
        self.timeout_seconds = timeout_seconds
        super().__init__(f"Run {run_id!r} exceeded max duration of {timeout_seconds}s")
