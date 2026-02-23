from __future__ import annotations

from typing import Any

from app.engine.templates import resolve_templates
from app.steps.base import StepHandler
from app.steps.registry import register_step


@register_step
class TransformHandler(StepHandler):
    step_type = "transform"

    async def run(self) -> dict[str, Any]:
        mapping: dict = self.config.get("mapping", {})
        return resolve_templates(mapping, self.context)
