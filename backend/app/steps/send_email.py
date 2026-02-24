from __future__ import annotations

from typing import Any

from app.steps.base import StepHandler
from app.steps.registry import register_step


@register_step
class SendEmailHandler(StepHandler):
    step_type = "send_email"
    metadata = {
        "label": "Send Email",
        "description": "Send an email to one or more recipients.",
        "config_schema": {
            "to": {"type": "string", "required": True},
            "subject": {"type": "string", "required": True},
            "body": {"type": "string", "required": True},
        },
    }

    async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        to: str | list[str] = config["to"]
        subject: str = config["subject"]
        body: str = config["body"]
        return {"sent_to": to, "subject": subject, "status": "queued"}
