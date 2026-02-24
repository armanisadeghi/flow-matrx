from __future__ import annotations

import re
from typing import Any

from jinja2 import Environment, StrictUndefined

_jinja_env = Environment(undefined=StrictUndefined)
_SINGLE_TEMPLATE = re.compile(r"^\{\{(.+?)\}\}$")
_HAS_TEMPLATE = re.compile(r"\{\{.+?\}\}")


def _deep_get(data: Any, path: str) -> Any:
    parts = path.split(".")
    current = data
    for part in parts:
        if isinstance(current, dict):
            current = current[part]
        elif isinstance(current, (list, tuple)):
            current = current[int(part)]
        else:
            raise KeyError(f"Cannot navigate into {type(current).__name__} with key {part!r}")
    return current


def resolve_templates(obj: Any, scope: dict[str, Any]) -> Any:
    if isinstance(obj, str):
        single = _SINGLE_TEMPLATE.match(obj.strip())
        if single:
            path = single.group(1).strip()
            if "|" not in path and "{%" not in path:
                return _deep_get(scope, path)

        if _HAS_TEMPLATE.search(obj):
            template = _jinja_env.from_string(obj)
            return template.render(**scope)
        return obj

    if isinstance(obj, dict):
        return {k: resolve_templates(v, scope) for k, v in obj.items()}
    if isinstance(obj, list):
        return [resolve_templates(item, scope) for item in obj]
    return obj


def extract_template_refs(obj: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(obj, str):
        for match in _HAS_TEMPLATE.finditer(obj):
            inner = match.group()[2:-2].strip()
            if "|" in inner:
                inner = inner.split("|")[0].strip()
            refs.add(inner)
    elif isinstance(obj, dict):
        for v in obj.values():
            refs |= extract_template_refs(v)
    elif isinstance(obj, list):
        for item in obj:
            refs |= extract_template_refs(item)
    return refs
