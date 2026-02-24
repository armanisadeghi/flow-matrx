from __future__ import annotations

from typing import Any

from app.engine.templates import resolve_templates
from app.steps.base import StepHandler
from app.steps.registry import register_step


@register_step
class TransformHandler(StepHandler):
    step_type = "transform"
    metadata = {
        "label": "Transform",
        "description": "Transform data using template-based field mapping.",
        "config_schema": {
            "mapping": {"type": "object", "required": True},
        },
    }

    async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        mapping: dict = config.get("mapping", {})
        result = resolve_templates(mapping, context)
        return result if isinstance(result, dict) else {"result": result}
