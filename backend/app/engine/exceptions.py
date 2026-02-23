"""Custom exceptions for the workflow engine."""


class PauseExecution(Exception):
    """Raised by a step that needs human approval before continuing."""

    def __init__(self, step_id: str, approval_prompt: str = "") -> None:
        self.step_id = step_id
        self.approval_prompt = approval_prompt
        super().__init__(f"Execution paused at step {step_id!r}")


class StepTimeout(Exception):
    """Raised when a step exceeds its configured timeout."""

    def __init__(self, step_id: str, timeout_seconds: int) -> None:
        self.step_id = step_id
        self.timeout_seconds = timeout_seconds
        super().__init__(
            f"Step {step_id!r} timed out after {timeout_seconds}s"
        )


class WorkflowValidationError(Exception):
    """Raised when a workflow definition fails validation."""
