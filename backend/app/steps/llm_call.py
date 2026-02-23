from __future__ import annotations

from typing import Any

import httpx

from app.config import settings
from app.steps.base import StepHandler
from app.steps.registry import register_step


@register_step
class LLMCallHandler(StepHandler):
    step_type = "llm_call"

    async def run(self) -> dict[str, Any]:
        provider: str = self.config.get("provider", "openai")
        model: str = self.config.get("model", "gpt-4o")
        messages: list = self.config.get("messages", [])
        temperature: float = float(self.config.get("temperature", 0.7))

        if provider == "openai":
            return await self._call_openai(model, messages, temperature)
        raise ValueError(f"Unsupported LLM provider: {provider}")

    async def _call_openai(
        self, model: str, messages: list, temperature: float
    ) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={"model": model, "messages": messages, "temperature": temperature},
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()
            return {
                "content": data["choices"][0]["message"]["content"],
                "model": data["model"],
                "usage": data.get("usage", {}),
            }
