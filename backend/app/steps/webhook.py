from __future__ import annotations

from typing import Any

import httpx

from app.steps.base import StepHandler
from app.steps.registry import register_step


@register_step
class WebhookHandler(StepHandler):
    step_type = "webhook"
    metadata = {
        "label": "Webhook",
        "description": "Send a webhook POST request to an external URL.",
        "config_schema": {
            "url": {"type": "string", "required": True},
            "payload": {"type": "object", "default": {}},
            "secret": {"type": "string", "default": ""},
        },
    }

    async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        url: str = config["url"]
        payload: dict = config.get("payload", {})
        secret: str = config.get("secret", "")
        headers: dict = {"Content-Type": "application/json"}
        if secret:
            headers["X-Webhook-Secret"] = secret

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            return {"status_code": response.status_code, "body": response.text}
