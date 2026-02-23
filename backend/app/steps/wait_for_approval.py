from __future__ import annotations

from typing import Any

from app.engine.exceptions import PauseExecution
from app.steps.base import StepHandler
from app.steps.registry import register_step


@register_step
class WaitForApprovalHandler(StepHandler):
    step_type = "wait_for_approval"

    async def run(self) -> dict[str, Any]:
        prompt: str = self.config.get("prompt", "Please review and approve to continue.")
        raise PauseExecution(step_id=self.step_id, approval_prompt=prompt)
