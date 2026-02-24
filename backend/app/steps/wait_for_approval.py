from __future__ import annotations

from typing import Any

from app.engine.exceptions import PauseExecution
from app.steps.base import StepHandler
from app.steps.registry import register_step


@register_step
class WaitForApprovalHandler(StepHandler):
    step_type = "wait_for_approval"
    metadata = {
        "label": "Wait for Approval",
        "description": "Pause execution and wait for human approval before continuing.",
        "config_schema": {
            "prompt": {"type": "string", "default": "Please review and approve to continue."},
        },
    }

    async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        prompt: str = config.get("prompt", "Please review and approve to continue.")
        raise PauseExecution(step_id="", reason=prompt)
