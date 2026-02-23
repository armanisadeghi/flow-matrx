"""WorkflowEngine — the execution loop.

Responsible for orchestrating step execution, managing parallel branches,
handling conditions, and emitting run events.
"""
from __future__ import annotations

import asyncio
from typing import Any
from uuid import UUID

import structlog

from app.engine.exceptions import PauseExecution, StepTimeout
from app.engine.graph import WorkflowGraph
from app.engine.templates import resolve_templates
from app.events.bus import event_bus
from app.steps.registry import STEP_REGISTRY

logger = structlog.get_logger(__name__)


class WorkflowEngine:
    def __init__(self, run_id: UUID, workflow_def: dict, db_conn: Any) -> None:
        self.run_id = run_id
        self.workflow_def = workflow_def
        self.db_conn = db_conn
        self.graph = WorkflowGraph(workflow_def["nodes"], workflow_def["edges"])
        self.context: dict[str, Any] = {}

    async def execute(self, trigger_payload: dict | None = None) -> None:
        if trigger_payload:
            self.context["trigger"] = trigger_payload

        await event_bus.emit("run.started", run_id=self.run_id)
        try:
            await self._run_graph()
            await event_bus.emit("run.completed", run_id=self.run_id)
        except PauseExecution:
            await event_bus.emit("run.paused", run_id=self.run_id)
        except Exception as exc:
            logger.exception("Workflow execution failed", run_id=str(self.run_id))
            await event_bus.emit("run.failed", run_id=self.run_id, error=str(exc))
            raise

    async def _run_graph(self) -> None:
        ready = self.graph.get_ready_steps(completed=set())
        completed: set[str] = set()

        while ready:
            await asyncio.gather(*[self._run_step(step_id) for step_id in ready])
            completed.update(ready)
            ready = self.graph.get_ready_steps(completed=completed)

    async def _run_step(self, step_id: str) -> None:
        node = self.graph.get_node(step_id)
        handler_cls = STEP_REGISTRY.get(node["type"])
        if handler_cls is None:
            raise ValueError(f"Unknown step type: {node['type']}")

        resolved_config = resolve_templates(node["config"], self.context)
        handler = handler_cls(step_id=step_id, config=resolved_config, context=self.context)

        await event_bus.emit("step.started", run_id=self.run_id, step_id=step_id)
        try:
            output = await handler.run()
            self.context[step_id] = output
            await event_bus.emit(
                "step.completed", run_id=self.run_id, step_id=step_id, output=output
            )
        except PauseExecution:
            await event_bus.emit(
                "step.waiting_approval", run_id=self.run_id, step_id=step_id
            )
            raise
        except StepTimeout as exc:
            await event_bus.emit(
                "step.failed", run_id=self.run_id, step_id=step_id, error=str(exc)
            )
            raise
