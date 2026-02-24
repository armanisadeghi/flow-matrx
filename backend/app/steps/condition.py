from __future__ import annotations

from typing import Any

from app.engine.safe_eval import safe_eval
from app.steps.base import StepHandler
from app.steps.registry import register_step


@register_step
class ConditionHandler(StepHandler):
    step_type = "condition"
    metadata = {
        "label": "Condition",
        "description": "Evaluate a boolean expression to determine branching.",
        "config_schema": {
            "expression": {"type": "string", "required": True},
        },
    }

    async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        expression: str = config["expression"]
        result = safe_eval(expression, context)
        return {"result": bool(result), "branch": "true" if result else "false"}
