from __future__ import annotations

from typing import Any

from app.steps.base import StepHandler
from app.steps.registry import register_step


@register_step
class DatabaseQueryHandler(StepHandler):
    step_type = "database_query"
    metadata = {
        "label": "Database Query",
        "description": "Execute a parameterized SQL query and return the result rows.",
        "config_schema": {
            "query": {"type": "string", "required": True},
            "params": {"type": "array", "default": []},
        },
    }

    async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        query: str = config["query"]
        params: list = config.get("params", [])
        conn = context.get("__db_conn__")
        if conn is None:
            raise RuntimeError("No database connection in context")
        rows = await conn.fetch(query, *params)
        return {"rows": [dict(row) for row in rows], "count": len(rows)}
