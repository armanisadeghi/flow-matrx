"""Step handler registry: maps step type names to handler classes."""
from __future__ import annotations

from app.steps.base import StepHandler

STEP_REGISTRY: dict[str, type[StepHandler]] = {}


def register_step(cls: type[StepHandler]) -> type[StepHandler]:
    """Decorator to register a step handler."""
    STEP_REGISTRY[cls.step_type] = cls
    return cls


# Import all handlers so they register themselves
from app.steps.http_request import HttpRequestHandler  # noqa: E402, F401
from app.steps.llm_call import LLMCallHandler  # noqa: E402, F401
from app.steps.inline_code import InlineCodeHandler  # noqa: E402, F401
from app.steps.condition import ConditionHandler  # noqa: E402, F401
from app.steps.database_query import DatabaseQueryHandler  # noqa: E402, F401
from app.steps.transform import TransformHandler  # noqa: E402, F401
from app.steps.wait_for_approval import WaitForApprovalHandler  # noqa: E402, F401
from app.steps.wait_for_event import WaitForEventHandler  # noqa: E402, F401
from app.steps.send_email import SendEmailHandler  # noqa: E402, F401
from app.steps.webhook import WebhookHandler  # noqa: E402, F401
from app.steps.delay import DelayHandler  # noqa: E402, F401
from app.steps.for_each import ForEachHandler  # noqa: E402, F401
