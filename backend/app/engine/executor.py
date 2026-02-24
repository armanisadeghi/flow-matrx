from __future__ import annotations

import asyncio
import time
from typing import Any
from uuid import UUID

import structlog

from app.engine.exceptions import EngineError, PauseExecution, StepTimeout
from app.engine.graph import WorkflowGraph
from app.engine.safe_eval import safe_eval
from app.engine.templates import resolve_templates
from app.events.bus import event_bus
from app.events.types import EventType
from app.steps.registry import STEP_REGISTRY

logger = structlog.get_logger(__name__)

MAX_OUTPUT_KEYS_FOR_DISPLAY = 5


def _truncate_for_display(output: dict[str, Any], max_keys: int = MAX_OUTPUT_KEYS_FOR_DISPLAY) -> dict[str, Any]:
    if not isinstance(output, dict) or len(output) <= max_keys:
        return output
    keys = list(output.keys())[:max_keys]
    result = {k: output[k] for k in keys}
    result["_truncated"] = True
    result["_total_keys"] = len(output)
    return result


def _calculate_backoff(strategy: str, base: float, attempt: int) -> float:
    match strategy:
        case "fixed":
            return base
        case "linear":
            return base * attempt
        case "exponential":
            return base ** attempt
        case _:
            return base


class WorkflowEngine:
    def __init__(self) -> None:
        pass

    async def execute_run(self, run_id: UUID) -> None:
        from app.db.models import (
            run_manager_instance as run_mgr,
            workflow_manager_instance as wf_mgr,
            step_run_manager_instance as sr_mgr,
        )

        run = await run_mgr.load_by_id(str(run_id))
        if run is None:
            raise EngineError(f"Run {run_id} not found")

        workflow = await wf_mgr.load_by_id(str(run.workflow_id))
        if workflow is None:
            raise EngineError(f"Workflow {run.workflow_id} not found")

        definition = workflow.definition
        graph = WorkflowGraph(definition["nodes"], definition["edges"])
        context: dict[str, Any] = dict(run.context) if run.context else {}

        if run.input:
            context["input"] = run.input

        await run_mgr.update_item(str(run_id), status="running", started_at="now()")
        await event_bus.emit(run_id, EventType.RUN_STARTED, payload={"status": "running"})

        start_time = time.monotonic()
        active_tasks: list[asyncio.Task[Any]] = []

        try:
            while True:
                fresh_run = await run_mgr.load_by_id(str(run_id))
                if fresh_run and fresh_run.status == "cancelled":
                    for task in active_tasks:
                        task.cancel()
                    await event_bus.emit(run_id, EventType.RUN_CANCELLED, payload={"status": "cancelled"})
                    return

                existing_step_runs = await sr_mgr.filter_items(run_id=str(run_id))
                done_ids: set[str] = set()
                for sr in existing_step_runs:
                    if sr.status in ("completed", "skipped"):
                        done_ids.add(sr.step_id)

                ready_nodes = graph.get_ready_steps(done_ids)
                if not ready_nodes:
                    break

                active_tasks = [
                    asyncio.create_task(
                        self._execute_step(run_id, node, context, graph)
                    )
                    for node in ready_nodes
                ]

                results = await asyncio.gather(*active_tasks, return_exceptions=True)
                active_tasks.clear()

                for node, result in zip(ready_nodes, results):
                    node_id = node["id"]
                    node_data = node.get("data", {})
                    on_error = node_data.get("on_error", "fail")

                    if isinstance(result, PauseExecution):
                        duration_ms = int((time.monotonic() - start_time) * 1000)
                        await run_mgr.update_item(str(run_id), status="paused", context=context)
                        await event_bus.emit(
                            run_id, EventType.RUN_PAUSED,
                            payload={
                                "status": "paused",
                                "waiting_step_id": result.step_id,
                                "reason": result.reason,
                                "duration_ms": duration_ms,
                            },
                        )
                        return

                    if isinstance(result, Exception):
                        if on_error == "skip":
                            await sr_mgr.create_item(
                                run_id=str(run_id), step_id=node_id,
                                step_type=node.get("type", "unknown"),
                                status="skipped", error=str(result), attempt=1,
                            )
                            await event_bus.emit(
                                run_id, EventType.STEP_SKIPPED, step_id=node_id,
                                payload={"step_id": node_id, "status": "skipped", "reason": str(result)},
                            )
                            continue

                        duration_ms = int((time.monotonic() - start_time) * 1000)
                        await run_mgr.update_item(
                            str(run_id), status="failed", error=str(result),
                            completed_at="now()", context=context,
                        )
                        await event_bus.emit(
                            run_id, EventType.RUN_FAILED,
                            payload={
                                "status": "failed",
                                "error": str(result),
                                "failed_step_id": node_id,
                                "duration_ms": duration_ms,
                            },
                        )
                        return

                    if isinstance(result, dict):
                        context[node_id] = result
                        await run_mgr.update_item(str(run_id), context=context)
                        await event_bus.emit(
                            run_id, EventType.CONTEXT_UPDATED, step_id=node_id,
                            payload={"step_id": node_id, "keys_added": list(result.keys())},
                        )

            duration_ms = int((time.monotonic() - start_time) * 1000)
            await run_mgr.update_item(
                str(run_id), status="completed", completed_at="now()", context=context,
            )
            await event_bus.emit(
                run_id, EventType.RUN_COMPLETED,
                payload={"status": "completed", "duration_ms": duration_ms},
            )

        except Exception as exc:
            duration_ms = int((time.monotonic() - start_time) * 1000)
            logger.exception("Unexpected engine failure", run_id=str(run_id))
            await run_mgr.update_item(
                str(run_id), status="failed", error=str(exc),
                completed_at="now()", context=context,
            )
            await event_bus.emit(
                run_id, EventType.RUN_FAILED,
                payload={"status": "failed", "error": str(exc), "duration_ms": duration_ms},
            )
        finally:
            for task in active_tasks:
                if not task.done():
                    task.cancel()

    async def _execute_step(
        self,
        run_id: UUID,
        node: dict[str, Any],
        context: dict[str, Any],
        graph: WorkflowGraph,
    ) -> dict[str, Any]:
        from app.db.models import step_run_manager_instance as sr_mgr

        node_id = node["id"]
        step_type = node.get("type", node.get("data", {}).get("type", "unknown"))
        node_data = node.get("data", {})
        step_label = node_data.get("label", node_id)
        config = node_data.get("config", {})

        if step_type == "condition":
            return await self._evaluate_condition(run_id, node, context, graph)

        if step_type == "wait_for_approval":
            await sr_mgr.create_item(
                run_id=str(run_id), step_id=node_id, step_type="wait_for_approval",
                status="waiting", input=config, attempt=1, started_at="now()",
            )
            await event_bus.emit(
                run_id, EventType.STEP_WAITING, step_id=node_id,
                payload={
                    "step_id": node_id, "step_type": step_type,
                    "status": "waiting", "waiting_for": "approval",
                    "label": step_label,
                },
            )
            raise PauseExecution(step_id=node_id, reason=config.get("prompt", "Approval required"))

        handler = STEP_REGISTRY.get(step_type)
        if handler is None:
            raise EngineError(f"No handler registered for step type: {step_type!r}")

        max_attempts = node_data.get("max_attempts", 1)
        backoff_strategy = node_data.get("backoff_strategy", "fixed")
        backoff_base = node_data.get("backoff_base", 2.0)
        timeout_seconds = node_data.get("timeout_seconds")

        resolved_config = resolve_templates(config, context)
        last_error: Exception | None = None

        for attempt in range(1, max_attempts + 1):
            await sr_mgr.create_item(
                run_id=str(run_id), step_id=node_id, step_type=step_type,
                status="running", input=resolved_config, attempt=attempt,
                started_at="now()",
            )
            await event_bus.emit(
                run_id, EventType.STEP_STARTED, step_id=node_id,
                payload={
                    "step_id": node_id, "step_type": step_type,
                    "step_label": step_label, "attempt": attempt,
                },
            )

            step_start = time.monotonic()
            try:
                coro = handler.execute(resolved_config, context)
                if timeout_seconds:
                    output = await asyncio.wait_for(coro, timeout=timeout_seconds)
                else:
                    output = await coro

                if not isinstance(output, dict):
                    output = {"result": output}

                step_duration = int((time.monotonic() - step_start) * 1000)
                await sr_mgr.update_item(
                    None,
                    _filter={"run_id": str(run_id), "step_id": node_id, "attempt": attempt},
                    status="completed", output=output, completed_at="now()",
                )
                await event_bus.emit(
                    run_id, EventType.STEP_COMPLETED, step_id=node_id,
                    payload={
                        "step_id": node_id, "step_type": step_type,
                        "status": "completed",
                        "output_summary": _truncate_for_display(output),
                        "duration_ms": step_duration,
                    },
                )
                return output

            except asyncio.TimeoutError:
                last_error = StepTimeout(node_id, timeout_seconds or 0)
                await sr_mgr.update_item(
                    None,
                    _filter={"run_id": str(run_id), "step_id": node_id, "attempt": attempt},
                    status="failed", error=str(last_error), completed_at="now()",
                )
            except Exception as exc:
                last_error = exc
                await sr_mgr.update_item(
                    None,
                    _filter={"run_id": str(run_id), "step_id": node_id, "attempt": attempt},
                    status="failed", error=str(exc), completed_at="now()",
                )

            will_retry = attempt < max_attempts
            if will_retry:
                backoff = _calculate_backoff(backoff_strategy, backoff_base, attempt)
                await event_bus.emit(
                    run_id, EventType.STEP_RETRYING, step_id=node_id,
                    payload={
                        "step_id": node_id, "attempt": attempt,
                        "max_attempts": max_attempts,
                        "backoff_seconds": backoff, "error": str(last_error),
                    },
                )
                await asyncio.sleep(backoff)

        await event_bus.emit(
            run_id, EventType.STEP_FAILED, step_id=node_id,
            payload={
                "step_id": node_id, "step_type": step_type,
                "status": "failed", "error": str(last_error),
                "attempt": max_attempts,
            },
        )
        if last_error is not None:
            raise last_error
        raise EngineError(f"Step {node_id} failed but no error was captured")

    async def _evaluate_condition(
        self,
        run_id: UUID,
        node: dict[str, Any],
        context: dict[str, Any],
        graph: WorkflowGraph,
    ) -> dict[str, Any]:
        from app.db.models import step_run_manager_instance as sr_mgr

        node_id = node["id"]
        node_data = node.get("data", {})
        config = node_data.get("config", {})
        expression = config.get("expression", "false")

        resolved_expr = resolve_templates(expression, context)
        if not isinstance(resolved_expr, str):
            resolved_expr = str(resolved_expr)

        await sr_mgr.create_item(
            run_id=str(run_id), step_id=node_id, step_type="condition",
            status="running", input={"expression": resolved_expr}, attempt=1,
            started_at="now()",
        )
        await event_bus.emit(
            run_id, EventType.STEP_STARTED, step_id=node_id,
            payload={
                "step_id": node_id, "step_type": "condition",
                "step_label": node_data.get("label", node_id), "attempt": 1,
            },
        )

        result = bool(safe_eval(resolved_expr, context))

        await sr_mgr.update_item(
            None,
            _filter={"run_id": str(run_id), "step_id": node_id, "attempt": 1},
            status="completed", output={"result": result}, completed_at="now()",
        )
        await event_bus.emit(
            run_id, EventType.STEP_COMPLETED, step_id=node_id,
            payload={
                "step_id": node_id, "step_type": "condition",
                "status": "completed", "output_summary": {"result": result},
                "duration_ms": 0,
            },
        )

        losing_branch = "false" if result else "true"
        skip_ids = graph.get_branch_nodes(node_id, losing_branch)

        for skip_id in skip_ids:
            await sr_mgr.create_item(
                run_id=str(run_id), step_id=skip_id,
                step_type=graph.get_node(skip_id).get("data", {}).get("type", "unknown"),
                status="skipped", attempt=1,
            )
            await event_bus.emit(
                run_id, EventType.STEP_SKIPPED, step_id=skip_id,
                payload={
                    "step_id": skip_id, "status": "skipped",
                    "reason": f"Condition {node_id} evaluated to {result}",
                },
            )

        return {"result": result}
