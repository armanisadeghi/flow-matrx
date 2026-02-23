from __future__ import annotations

from typing import Any

import httpx

from app.steps.base import StepHandler
from app.steps.registry import register_step


@register_step
class HttpRequestHandler(StepHandler):
    step_type = "http_request"

    async def run(self) -> dict[str, Any]:
        method: str = self.config.get("method", "GET").upper()
        url: str = self.config["url"]
        headers: dict = self.config.get("headers", {})
        body: Any = self.config.get("body")
        timeout: float = float(self.config.get("timeout_seconds", 30))

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(method, url, headers=headers, json=body)
            response.raise_for_status()
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
            }
