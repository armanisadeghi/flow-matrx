from __future__ import annotations

from typing import Any

from app.steps.base import StepHandler
from app.steps.registry import register_step


@register_step
class WaitForEventHandler(StepHandler):
    step_type = "wait_for_event"
    metadata = {
        "label": "Wait for Event",
        "description": "Wait for an external event before continuing execution.",
        "config_schema": {
            "event_name": {"type": "string", "required": True},
        },
    }

    async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        event_name: str = config["event_name"]
        return {"waiting_for": event_name}
