from __future__ import annotations

from typing import Any

import httpx

from app.steps.base import StepHandler
from app.steps.registry import register_step


@register_step
class SendEmailHandler(StepHandler):
    step_type = "send_email"

    async def run(self) -> dict[str, Any]:
        to: str | list[str] = self.config["to"]
        subject: str = self.config["subject"]
        body: str = self.config["body"]
        # Placeholder: integrate with an email provider (e.g., Resend, SendGrid)
        return {"sent_to": to, "subject": subject, "status": "queued"}
