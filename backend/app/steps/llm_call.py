from __future__ import annotations

from typing import Any

import httpx

from app.config import settings
from app.steps.base import StepHandler
from app.steps.registry import register_step


# From Arman: This is only a placeholder. No need to make updates, since it will be reaplced with our real implementation.

@register_step
class LLMCallHandler(StepHandler):
    step_type = "llm_call"
    metadata = {
        "label": "LLM Call",
        "description": "Call a large language model and return the generated text.",
        "config_schema": {
            "provider": {"type": "string", "default": "openai"},
            "model": {"type": "string", "default": "gpt-4o"},
            "messages": {"type": "array", "required": True},
            "temperature": {"type": "number", "default": 0.7},
        },
    }

    async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        provider: str = config.get("provider", "openai")
        model: str = config.get("model", "gpt-4o")
        messages: list = config.get("messages", [])
        temperature: float = float(config.get("temperature", 0.7))

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
