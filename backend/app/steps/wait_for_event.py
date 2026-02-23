from __future__ import annotations

from typing import Any

from app.steps.base import StepHandler
from app.steps.registry import register_step


@register_step
class WaitForEventHandler(StepHandler):
    step_type = "wait_for_event"

    async def run(self) -> dict[str, Any]:
        event_name: str = self.config["event_name"]
        # Actual wait logic is handled by the engine via a Redis subscription.
        # This handler simply records what event it is waiting for.
        return {"waiting_for": event_name}
