from __future__ import annotations

import asyncio
from typing import Any

from app.steps.base import StepHandler
from app.steps.registry import register_step


@register_step
class InlineCodeHandler(StepHandler):
    step_type = "inline_code"

    async def run(self) -> dict[str, Any]:
        code: str = self.config["code"]
        timeout: float = float(self.config.get("timeout_seconds", 30))
        input_vars: dict = self.config.get("input_vars", {})

        loop = asyncio.get_running_loop()
        return await asyncio.wait_for(
            loop.run_in_executor(None, self._execute_sync, code, input_vars),
            timeout=timeout,
        )

    def _execute_sync(self, code: str, input_vars: dict) -> dict[str, Any]:
        local_vars: dict[str, Any] = {"input": input_vars, "output": {}}
        exec(code, {"__builtins__": __builtins__}, local_vars)  # noqa: S102
        return local_vars.get("output", {})
