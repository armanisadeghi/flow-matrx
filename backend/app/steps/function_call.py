from __future__ import annotations

from typing import Any

from app.engine.function_registry import FunctionNotFoundError, function_registry
from app.steps.base import StepHandler
from app.steps.registry import register_step


@register_step
class FunctionCallHandler(StepHandler):
    step_type = "function_call"
    metadata = {
        "label": "Function Call",
        "description": "Execute a registered Python function by name.",
        "config_schema": {
            "function_name": {"type": "string", "required": True},
            "args": {"type": "object", "default": {}},
        },
    }

    async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        function_name: str = config["function_name"]
        args: dict[str, Any] = config.get("args", {})

        if not function_registry.has(function_name):
            raise FunctionNotFoundError(
                f"Function {function_name!r} is not registered. "
                f"Available: {', '.join(function_registry.registered_names) or '(none)'}"
            )

        func = function_registry.get(function_name)
        merged_config = {**config, **args}
        output = await func(merged_config, context)

        if not isinstance(output, dict):
            output = {"result": output}

        return self.validate_output(output)
