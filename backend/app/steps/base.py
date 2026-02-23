"""Abstract base class for all step handlers."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class StepHandler(ABC):
    step_type: str = ""

    def __init__(self, step_id: str, config: dict[str, Any], context: dict[str, Any]) -> None:
        self.step_id = step_id
        self.config = config
        self.context = context

    @abstractmethod
    async def run(self) -> dict[str, Any]:
        """Execute the step and return its output."""
        ...
