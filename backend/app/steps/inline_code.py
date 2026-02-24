from __future__ import annotations

import asyncio
import json
import math
from typing import Any

from app.steps.base import StepHandler
from app.steps.registry import register_step


# Safe builtins for sandboxed code execution
SAFE_BUILTINS = {
    # Basic types and operations
    "abs": abs,
    "all": all,
    "any": any,
    "bool": bool,
    "dict": dict,
    "enumerate": enumerate,
    "filter": filter,
    "float": float,
    "int": int,
    "len": len,
    "list": list,
    "map": map,
    "max": max,
    "min": min,
    "range": range,
    "round": round,
    "set": set,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "tuple": tuple,
    "type": type,
    "zip": zip,

    # String operations
    "isinstance": isinstance,
    "isinstance": isinstance,
    "ord": ord,
    "chr": chr,
    "repr": repr,

    # Math operations
    "math": math,

    # JSON operations
    "json_dumps": json.dumps,
    "json_loads": json.loads,
}


@register_step
class InlineCodeHandler(StepHandler):
    step_type = "inline_code"
    metadata = {
        "label": "Inline Code",
        "description": "Execute a Python code snippet in a sandboxed environment.",
        "config_schema": {
            "code": {"type": "string", "required": True},
            "timeout_seconds": {"type": "number", "default": 30},
        },
    }
    CONTEXT_FIELDS = {"result"}

    async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        code: str = config["code"]
        timeout: float = float(config.get("timeout_seconds", 30))

        loop = asyncio.get_running_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(None, self._execute_sync, code, context),
            timeout=timeout,
        )

        # Validate that result was set
        if result.get("result") is None:
            raise ValueError("Inline code must set the 'result' variable")

        return self.validate_output(result)

    @staticmethod
    def _execute_sync(code: str, context: dict[str, Any]) -> dict[str, Any]:
        # Create input from resolved config (templates already filled by engine)
        input_data = context.get("input", {})

        # Initialize local variables that code can access
        local_vars: dict[str, Any] = {
            "context": context,
            "input": input_data,
            "result": None,  # Code must set this
        }

        # Execute with restricted builtins
        exec(code, {"__builtins__": SAFE_BUILTINS}, local_vars)  # noqa: S102

        # Return all local variables (including result)
        return {k: v for k, v in local_vars.items() if not k.startswith('_')}
