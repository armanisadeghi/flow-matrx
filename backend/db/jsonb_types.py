# Hand-authored. Never touched by the generator.
#
# One dataclass per JSONB field in models.py. The defaults here are
# structurally open (dict/list catch-alls) so behaviour is identical to
# bare JSONBField — customize any class freely to add strict typing.
#
# Naming convention: {ModelName}{FieldName} in PascalCase.
# When the generator is updated it will import from this file by name,
# so renaming a class here requires a matching update in models.py.
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Org
# ---------------------------------------------------------------------------


@dataclass
class OrgMetadata:
    extra: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# UserProfile
# ---------------------------------------------------------------------------


@dataclass
class UserProfileMetadata:
    extra: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# WfWorkflow
# ---------------------------------------------------------------------------


@dataclass
class WfWorkflowDefinition:
    nodes: list[Any] = field(default_factory=list)
    edges: list[Any] = field(default_factory=list)


@dataclass
class WfWorkflowInputSchema:
    extra: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# WfRun
# ---------------------------------------------------------------------------


@dataclass
class WfRunInput:
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class WfRunContext:
    extra: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# WfRunEvent
# ---------------------------------------------------------------------------


@dataclass
class WfRunEventPayload:
    extra: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# WfStepRun
# ---------------------------------------------------------------------------


@dataclass
class WfStepRunInput:
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class WfStepRunOutput:
    extra: dict[str, Any] = field(default_factory=dict)
