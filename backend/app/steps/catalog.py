from __future__ import annotations

from typing import Any

from app.steps.registry import STEP_REGISTRY


def get_step_catalog() -> list[dict[str, Any]]:
    """Return metadata for all registered step types for the frontend palette."""
    catalog = []
    for step_type, handler in STEP_REGISTRY.items():
        metadata = handler.metadata.copy()
        metadata["type"] = step_type
        catalog.append(metadata)

    # Sort by type for consistent ordering
    return sorted(catalog, key=lambda x: x["type"])