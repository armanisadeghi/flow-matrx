from __future__ import annotations

import asyncio
from typing import Any

from app.steps.base import StepHandler
from app.steps.registry import register_step


@register_step
class DelayHandler(StepHandler):
    step_type = "delay"

    async def run(self) -> dict[str, Any]:
        seconds: float = float(self.config.get("seconds", 0))
        await asyncio.sleep(seconds)
        return {"delayed_seconds": seconds}
