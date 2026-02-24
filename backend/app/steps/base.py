from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any


class StepHandler(ABC):
    step_type: str = ""
    metadata: dict[str, Any] = {}
    MAX_OUTPUT_SIZE: int = 100_000  # 100KB default
    CONTEXT_FIELDS: set[str] = set()  # Fields to keep when truncating

    @abstractmethod
    async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Execute the step. Returns JSON-serializable output."""

    def validate_output(self, output: Any) -> Any:
        """Ensure output isn't too large for the context dict."""
        # First ensure it's JSON serializable
        try:
            json_str = json.dumps(output, default=str)
            size = len(json_str.encode('utf-8'))
        except (TypeError, ValueError) as e:
            raise ValueError(f"Step output is not JSON serializable: {e}") from e

        if size > self.MAX_OUTPUT_SIZE:
            if self.CONTEXT_FIELDS:
                # Truncate by keeping only specified fields
                if isinstance(output, dict):
                    truncated = {k: v for k, v in output.items() if k in self.CONTEXT_FIELDS}
                    # Re-check size after truncation
                    try:
                        json_str = json.dumps(truncated, default=str)
                        if len(json_str.encode('utf-8')) <= self.MAX_OUTPUT_SIZE:
                            return truncated
                    except (TypeError, ValueError):
                        pass

            # If truncation didn't work or no fields specified, raise error
            raise ValueError(
                f"Step output too large: {size} bytes (max {self.MAX_OUTPUT_SIZE}). "
                f"Consider reducing output size or updating CONTEXT_FIELDS."
            )

        return output
