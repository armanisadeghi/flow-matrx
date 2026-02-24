from __future__ import annotations

from typing import Any

from app.steps.base import StepHandler
from app.steps.registry import register_step


@register_step
class ForEachHandler(StepHandler):
    step_type = "for_each"
    metadata = {
        "label": "For Each",
        "description": "Iterate over a list of items. Sub-workflow execution is orchestrated by the engine.",
        "config_schema": {
            "items": {"type": "array", "required": True},
        },
    }

    async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        items: list = config["items"]
        return {"items": items, "count": len(items), "results": []}
