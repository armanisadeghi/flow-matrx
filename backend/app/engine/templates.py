"""Template resolution: replaces {{step_id.field}} references in configs."""
from __future__ import annotations

import re
from typing import Any

from jinja2 import Environment, StrictUndefined

_jinja_env = Environment(undefined=StrictUndefined)
_TEMPLATE_PATTERN = re.compile(r"\{\{[^}]+\}\}")


def resolve_templates(config: Any, context: dict[str, Any]) -> Any:
    """Recursively resolve Jinja2 templates in config values."""
    if isinstance(config, str):
        if _TEMPLATE_PATTERN.search(config):
            template = _jinja_env.from_string(config)
            return template.render(**context)
        return config
    if isinstance(config, dict):
        return {k: resolve_templates(v, context) for k, v in config.items()}
    if isinstance(config, list):
        return [resolve_templates(item, context) for item in config]
    return config


def extract_template_refs(config: Any) -> list[str]:
    """Extract all {{ref}} identifiers from a config for validation."""
    refs: list[str] = []
    if isinstance(config, str):
        for match in _TEMPLATE_PATTERN.finditer(config):
            inner = match.group()[2:-2].strip()
            refs.append(inner)
    elif isinstance(config, dict):
        for v in config.values():
            refs.extend(extract_template_refs(v))
    elif isinstance(config, list):
        for item in config:
            refs.extend(extract_template_refs(item))
    return refs
