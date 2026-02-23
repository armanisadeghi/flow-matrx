from __future__ import annotations

from typing import Any

from app.steps.base import StepHandler
from app.steps.registry import register_step


@register_step
class DatabaseQueryHandler(StepHandler):
    step_type = "database_query"

    async def run(self) -> dict[str, Any]:
        query: str = self.config["query"]
        params: list = self.config.get("params", [])
        conn = self.context.get("__db_conn__")
        if conn is None:
            raise RuntimeError("No database connection in context")
        rows = await conn.fetch(query, *params)
        return {"rows": [dict(row) for row in rows], "count": len(rows)}
