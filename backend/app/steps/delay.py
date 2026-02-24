from __future__ import annotations

import asyncio
from typing import Any

from app.steps.base import StepHandler
from app.steps.registry import register_step


@register_step
class DelayHandler(StepHandler):
    step_type = "delay"
    metadata = {
        "label": "Delay",
        "description": "Pause execution for a specified number of seconds.",
        "config_schema": {
            "seconds": {"type": "number", "required": True},
        },
    }

    async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        seconds: float = float(config.get("seconds", 0))
        await asyncio.sleep(seconds)
        return {"delayed_seconds": seconds}
