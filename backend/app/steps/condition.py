from __future__ import annotations

from typing import Any

from app.engine.safe_eval import safe_eval
from app.steps.base import StepHandler
from app.steps.registry import register_step


@register_step
class ConditionHandler(StepHandler):
    step_type = "condition"

    async def run(self) -> dict[str, Any]:
        expression: str = self.config["expression"]
        result = safe_eval(expression, self.context)
        return {"result": bool(result), "branch": "true" if result else "false"}
