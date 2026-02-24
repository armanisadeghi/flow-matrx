from __future__ import annotations

from typing import Any

from app.steps.base import StepHandler

STEP_REGISTRY: dict[str, StepHandler] = {}


def register_step(cls: type[StepHandler]) -> type[StepHandler]:
    STEP_REGISTRY[cls.step_type] = cls()
    return cls


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


STEP_CATALOG: list[dict[str, Any]] = [
    {"type": "http_request", "label": "HTTP Request", "icon": "globe", "category": "integrations", "description": "Send an HTTP request to an external URL and return the response."},
    {"type": "llm_call", "label": "LLM Call", "icon": "brain", "category": "ai", "description": "Call a large language model and return the generated text."},
    {"type": "inline_code", "label": "Code", "icon": "code", "category": "logic", "description": "Execute a Python code snippet in a sandboxed environment."},
    {"type": "condition", "label": "Condition", "icon": "git-branch", "category": "logic", "description": "Evaluate a boolean expression to determine branching."},
    {"type": "database_query", "label": "Database Query", "icon": "database", "category": "data", "description": "Execute a parameterized SQL query and return the result rows."},
    {"type": "transform", "label": "Transform", "icon": "shuffle", "category": "data", "description": "Transform data using template-based field mapping."},
    {"type": "delay", "label": "Delay", "icon": "clock", "category": "flow", "description": "Pause execution for a specified number of seconds."},
    {"type": "wait_for_approval", "label": "Approval", "icon": "user-check", "category": "flow", "description": "Pause execution and wait for human approval before continuing."},
    {"type": "wait_for_event", "label": "Wait for Event", "icon": "bell", "category": "flow", "description": "Wait for an external event before continuing execution."},
    {"type": "send_email", "label": "Send Email", "icon": "mail", "category": "integrations", "description": "Send an email to one or more recipients."},
    {"type": "webhook", "label": "Webhook", "icon": "webhook", "category": "integrations", "description": "Send a webhook POST request to an external URL."},
    {"type": "for_each", "label": "For Each", "icon": "repeat", "category": "logic", "description": "Iterate over a list of items, executing a sub-step for each."},
]
