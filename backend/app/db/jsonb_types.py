# Hand-authored. Never touched by the generator.
#
# One dataclass per JSONB field in models.py. The defaults here are
# structurally open (dict/list catch-alls) so behaviour is identical to
# bare JSONBField — customize any class freely to add strict typing.
#
# Naming convention: {ModelName}{FieldName} in PascalCase.
# When the generator is updated it will import from this file by name,
# so renaming a class here requires a matching update in models.py.
#
# OpenDict: used for JSONB fields whose structure is entirely user-driven
# (workflow context, step inputs/outputs, event payloads). These absorb
# any keys from the DB without raising on unknown fields.
from dataclasses import dataclass, field
from typing import Any


class OpenDict(dict):  # type: ignore[type-arg]
    """A plain dict subclass used as a TypedJSONBField type for open-ended JSONB.

    TypedJSONBField.to_python() calls ``OpenDict(**raw_dict)`` which is just
    ``dict(**raw_dict)`` — a no-op wrapper that preserves all keys.  The field
    stores and retrieves it as a plain dict so the engine can do
    ``context[step_id] = output`` freely.
    """


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


# WfWorkflowInputSchema is user-defined JSON Schema — open structure, not fixed fields
WfWorkflowInputSchema = OpenDict


# ---------------------------------------------------------------------------
# WfRun — context and input are open dicts (keyed by step_id / user keys)
# ---------------------------------------------------------------------------

WfRunInput = OpenDict
WfRunContext = OpenDict

# ---------------------------------------------------------------------------
# WfRunEvent — payload is open (engine-defined per event type)
# ---------------------------------------------------------------------------

WfRunEventPayload = OpenDict

# ---------------------------------------------------------------------------
# WfStepRun — input/output are open dicts (step-type-specific shapes)
# ---------------------------------------------------------------------------

WfStepRunInput = OpenDict
WfStepRunOutput = OpenDict
