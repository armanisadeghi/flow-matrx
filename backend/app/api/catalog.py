from __future__ import annotations

from fastapi import APIRouter

from app.db.schemas import StepTypeInfo
from app.steps.registry import STEP_CATALOG, STEP_REGISTRY

router = APIRouter()


@router.get("/steps", response_model=list[StepTypeInfo])
async def list_step_types() -> list[StepTypeInfo]:
    result: list[StepTypeInfo] = []
    for entry in STEP_CATALOG:
        handler = STEP_REGISTRY.get(entry["type"])
        config_schema = getattr(handler, "metadata", {}).get("config_schema", {}) if handler else {}
        result.append(
            StepTypeInfo(
                type=entry["type"],
                label=entry["label"],
                icon=entry["icon"],
                category=entry["category"],
                description=entry["description"],
                config_schema=config_schema,
            )
        )
    return result
