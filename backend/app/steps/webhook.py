from __future__ import annotations

from typing import Any

import httpx

from app.steps.base import StepHandler
from app.steps.registry import register_step


@register_step
class WebhookHandler(StepHandler):
    step_type = "webhook"

    async def run(self) -> dict[str, Any]:
        url: str = self.config["url"]
        payload: dict = self.config.get("payload", {})
        secret: str = self.config.get("secret", "")
        headers: dict = {"Content-Type": "application/json"}
        if secret:
            headers["X-Webhook-Secret"] = secret

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            return {"status_code": response.status_code, "body": response.text}
