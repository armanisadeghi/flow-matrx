from __future__ import annotations

import asyncio
from typing import Any

from app.steps.base import StepHandler
from app.steps.registry import register_step


@register_step
class ForEachHandler(StepHandler):
    step_type = "for_each"

    async def run(self) -> dict[str, Any]:
        items: list = self.config["items"]
        # Sub-workflow execution per item is orchestrated by the engine.
        # This handler returns the items list for iteration tracking.
        return {"items": items, "count": len(items), "results": []}
