from __future__ import annotations

import asyncio
import time
from typing import Any
from uuid import UUID

import structlog

from app.engine.exceptions import (
    EngineError,
    NonRetriableError,
    PauseExecution,
    RunCancelled,
    RunTimeout,
    StepTimeout,
)
from app.engine.graph import WorkflowGraph
from app.engine.safe_eval import safe_eval
from app.engine.templates import resolve_templates
from app.events.bus import EventBus, event_bus
from app.events.types import EventType
from app.steps.registry import STEP_REGISTRY

logger = structlog.get_logger(__name__)

MAX_OUTPUT_KEYS_FOR_DISPLAY = 5

# Engine-handled step types that bypass the generic handler path
_PAUSE_STEP_TYPES = frozenset({"wait_for_approval", "wait_for_event"})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _truncate_for_display(
    output: dict[str, Any], max_keys: int = MAX_OUTPUT_KEYS_FOR_DISPLAY
) -> dict[str, Any]:
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
            return min(base ** attempt, 300.0)  # cap at 5 minutes
        case _:
            return base


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class WorkflowEngine:
    """Executes a workflow run as an async loop over the DAG.

    Features:
        - Parallel execution of independent steps with concurrency limit
        - Retry with configurable backoff (fixed / linear / exponential)
        - Condition branching with subtree skipping
        - Pause / resume for approval and external-event steps
        - for_each loop execution with sub-step iteration
        - Per-step and per-run timeouts
        - Checkpoint after every batch (context saved to DB)
        - Idempotent: calling execute_run on a partially-completed run
          picks up where it left off
        - Cancellation check between batches
    """

    def __init__(
        self,
        bus: EventBus | None = None,
        max_concurrency: int = 10,
        run_timeout_seconds: float | None = None,
    ) -> None:
        self._bus = bus or event_bus
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._run_timeout = run_timeout_seconds

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    async def execute_run(self, run_id: UUID) -> None:
        from app.db.models import (
            run_manager_instance as run_mgr,
            step_run_manager_instance as sr_mgr,
            workflow_manager_instance as wf_mgr,
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

        # Only emit RUN_STARTED if we are starting fresh (not resuming).
        is_resume = run.status in ("paused", "running")
        if not is_resume:
            await run_mgr.update_item(str(run_id), status="running", started_at="now()")
            await self._bus.emit(
                run_id, EventType.RUN_STARTED, payload={"status": "running"}
            )
        else:
            await run_mgr.update_item(str(run_id), status="running")

        start_time = time.monotonic()
        active_tasks: list[asyncio.Task[Any]] = []

        try:
            while True:
                # -- cancellation check ------------------------------------
                await self._check_cancelled(run_id, active_tasks)

                # -- run-level timeout check -------------------------------
                if self._run_timeout:
                    elapsed = time.monotonic() - start_time
                    if elapsed > self._run_timeout:
                        raise RunTimeout(str(run_id), self._run_timeout)

                # -- determine completed / skipped steps -------------------
                existing_step_runs = await sr_mgr.filter_items(run_id=str(run_id))
                done_ids: set[str] = set()
                for sr in existing_step_runs:
                    if sr.status in ("completed", "skipped"):
                        done_ids.add(sr.step_id)

                # -- find next batch of ready steps -----------------------
                ready_nodes = graph.get_ready_steps(done_ids)
                if not ready_nodes:
                    break

                # -- execute batch in parallel (with semaphore) -----------
                active_tasks = [
                    asyncio.create_task(
                        self._guarded_execute_step(run_id, node, context, graph)
                    )
                    for node in ready_nodes
                ]

                results = await asyncio.gather(*active_tasks, return_exceptions=True)
                active_tasks.clear()

                # -- process results --------------------------------------
                for node, result in zip(ready_nodes, results):
                    node_id = node["id"]
                    node_data = node.get("data", {})
                    on_error = node_data.get("on_error", "fail")

                    # Pause (approval / external event)
                    if isinstance(result, PauseExecution):
                        duration_ms = int((time.monotonic() - start_time) * 1000)
                        await run_mgr.update_item(
                            str(run_id), status="paused", context=context,
                        )
                        await self._bus.emit(
                            run_id,
                            EventType.RUN_PAUSED,
                            payload={
                                "status": "paused",
                                "waiting_step_id": result.step_id,
                                "reason": result.reason,
                                "duration_ms": duration_ms,
                            },
                        )
                        return

                    # Cancellation bubbled up
                    if isinstance(result, (RunCancelled, asyncio.CancelledError)):
                        await self._bus.emit(
                            run_id,
                            EventType.RUN_CANCELLED,
                            payload={"status": "cancelled"},
                        )
                        return

                    # Error handling
                    if isinstance(result, Exception):
                        if on_error == "skip":
                            step_type = graph.get_node_type(node_id)
                            await sr_mgr.create_item(
                                run_id=str(run_id),
                                step_id=node_id,
                                step_type=step_type,
                                status="skipped",
                                error=str(result),
                                attempt=1,
                            )
                            await self._bus.emit(
                                run_id,
                                EventType.STEP_SKIPPED,
                                step_id=node_id,
                                payload={
                                    "step_id": node_id,
                                    "status": "skipped",
                                    "reason": str(result),
                                },
                            )
                            done_ids.add(node_id)
                            continue

                        if on_error == "continue":
                            context[node_id] = {"_error": str(result)}
                            await run_mgr.update_item(str(run_id), context=context)
                            done_ids.add(node_id)
                            continue

                        # Default: fail the run
                        duration_ms = int((time.monotonic() - start_time) * 1000)
                        await run_mgr.update_item(
                            str(run_id),
                            status="failed",
                            error=str(result),
                            completed_at="now()",
                            context=context,
                        )
                        await self._bus.emit(
                            run_id,
                            EventType.RUN_FAILED,
                            payload={
                                "status": "failed",
                                "error": str(result),
                                "failed_step_id": node_id,
                                "duration_ms": duration_ms,
                            },
                        )
                        return

                    # Success — merge output into context
                    if isinstance(result, dict):
                        context[node_id] = result
                        await run_mgr.update_item(str(run_id), context=context)
                        await self._bus.emit(
                            run_id,
                            EventType.CONTEXT_UPDATED,
                            step_id=node_id,
                            payload={
                                "step_id": node_id,
                                "keys_added": list(result.keys()),
                            },
                        )

            # -- all steps done --------------------------------------------
            duration_ms = int((time.monotonic() - start_time) * 1000)
            await run_mgr.update_item(
                str(run_id),
                status="completed",
                completed_at="now()",
                context=context,
            )
            await self._bus.emit(
                run_id,
                EventType.RUN_COMPLETED,
                payload={"status": "completed", "duration_ms": duration_ms},
            )

        except RunTimeout as exc:
            duration_ms = int((time.monotonic() - start_time) * 1000)
            logger.error("Run timed out", run_id=str(run_id), timeout=self._run_timeout)
            await run_mgr.update_item(
                str(run_id),
                status="failed",
                error=str(exc),
                completed_at="now()",
                context=context,
            )
            await self._bus.emit(
                run_id,
                EventType.RUN_FAILED,
                payload={
                    "status": "failed",
                    "error": str(exc),
                    "duration_ms": duration_ms,
                },
            )

        except RunCancelled:
            await self._bus.emit(
                run_id, EventType.RUN_CANCELLED, payload={"status": "cancelled"}
            )

        except Exception as exc:
            duration_ms = int((time.monotonic() - start_time) * 1000)
            logger.exception("Unexpected engine failure", run_id=str(run_id))
            await run_mgr.update_item(
                str(run_id),
                status="failed",
                error=str(exc),
                completed_at="now()",
                context=context,
            )
            await self._bus.emit(
                run_id,
                EventType.RUN_FAILED,
                payload={
                    "status": "failed",
                    "error": str(exc),
                    "duration_ms": duration_ms,
                },
            )

        finally:
            for task in active_tasks:
                if not task.done():
                    task.cancel()

    # ------------------------------------------------------------------
    # Concurrency-guarded step execution
    # ------------------------------------------------------------------

    async def _guarded_execute_step(
        self,
        run_id: UUID,
        node: dict[str, Any],
        context: dict[str, Any],
        graph: WorkflowGraph,
    ) -> dict[str, Any]:
        async with self._semaphore:
            return await self._execute_step(run_id, node, context, graph)

    # ------------------------------------------------------------------
    # Step execution (single step with retries)
    # ------------------------------------------------------------------

    async def _execute_step(
        self,
        run_id: UUID,
        node: dict[str, Any],
        context: dict[str, Any],
        graph: WorkflowGraph,
    ) -> dict[str, Any]:
        from app.db.models import step_run_manager_instance as sr_mgr

        node_id = node["id"]
        step_type = graph.get_node_type(node_id)
        node_data = graph.get_node_data(node_id)
        step_label = node_data.get("label", node_id)
        config = node_data.get("config", {})

        # -- Condition branching (engine-handled) --------------------------
        if step_type == "condition":
            return await self._evaluate_condition(run_id, node_id, context, graph)

        # -- Pause-type steps (approval / wait_for_event) ------------------
        if step_type in _PAUSE_STEP_TYPES:
            return await self._handle_pause_step(
                run_id, node_id, step_type, step_label, config
            )

        # -- for_each loop -------------------------------------------------
        if step_type == "for_each":
            return await self._execute_for_each(
                run_id, node_id, config, context, graph
            )

        # -- Regular handler execution -------------------------------------
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
                run_id=str(run_id),
                step_id=node_id,
                step_type=step_type,
                status="running",
                input=resolved_config,
                attempt=attempt,
                started_at="now()",
            )
            await self._bus.emit(
                run_id,
                EventType.STEP_STARTED,
                step_id=node_id,
                payload={
                    "step_id": node_id,
                    "step_type": step_type,
                    "step_label": step_label,
                    "attempt": attempt,
                },
            )

            step_start = time.monotonic()
            try:
                coro = handler.execute(resolved_config, context)
                if timeout_seconds:
                    output = await asyncio.wait_for(coro, timeout=timeout_seconds)
                else:
                    output = await coro

                # Handlers that raise PauseExecution (e.g. wait_for_event)
                # will be caught by the outer exception handler — but some
                # may want to return normally, so we handle both paths.

                if not isinstance(output, dict):
                    output = {"result": output}

                step_duration = int((time.monotonic() - step_start) * 1000)
                await sr_mgr.update_item(
                    None,
                    _filter={
                        "run_id": str(run_id),
                        "step_id": node_id,
                        "attempt": attempt,
                    },
                    status="completed",
                    output=output,
                    completed_at="now()",
                )
                await self._bus.emit(
                    run_id,
                    EventType.STEP_COMPLETED,
                    step_id=node_id,
                    payload={
                        "step_id": node_id,
                        "step_type": step_type,
                        "status": "completed",
                        "output_summary": _truncate_for_display(output),
                        "duration_ms": step_duration,
                    },
                )
                return output

            except PauseExecution as pause:
                # Handler raised PauseExecution (e.g. wait_for_event)
                pause.step_id = node_id
                raise

            except NonRetriableError:
                raise

            except asyncio.TimeoutError:
                last_error = StepTimeout(node_id, timeout_seconds or 0)
                await sr_mgr.update_item(
                    None,
                    _filter={
                        "run_id": str(run_id),
                        "step_id": node_id,
                        "attempt": attempt,
                    },
                    status="failed",
                    error=str(last_error),
                    completed_at="now()",
                )

            except Exception as exc:
                last_error = exc
                await sr_mgr.update_item(
                    None,
                    _filter={
                        "run_id": str(run_id),
                        "step_id": node_id,
                        "attempt": attempt,
                    },
                    status="failed",
                    error=str(exc),
                    completed_at="now()",
                )

            # Retry logic
            will_retry = attempt < max_attempts
            if will_retry:
                backoff = _calculate_backoff(backoff_strategy, backoff_base, attempt)
                await self._bus.emit(
                    run_id,
                    EventType.STEP_RETRYING,
                    step_id=node_id,
                    payload={
                        "step_id": node_id,
                        "attempt": attempt,
                        "max_attempts": max_attempts,
                        "backoff_seconds": backoff,
                        "error": str(last_error),
                    },
                )
                await asyncio.sleep(backoff)

        # All attempts exhausted
        await self._bus.emit(
            run_id,
            EventType.STEP_FAILED,
            step_id=node_id,
            payload={
                "step_id": node_id,
                "step_type": step_type,
                "status": "failed",
                "error": str(last_error),
                "attempt": max_attempts,
            },
        )
        if last_error is not None:
            raise last_error
        raise EngineError(f"Step {node_id} failed but no error was captured")

    # ------------------------------------------------------------------
    # Condition evaluation
    # ------------------------------------------------------------------

    async def _evaluate_condition(
        self,
        run_id: UUID,
        node_id: str,
        context: dict[str, Any],
        graph: WorkflowGraph,
    ) -> dict[str, Any]:
        from app.db.models import step_run_manager_instance as sr_mgr

        node_data = graph.get_node_data(node_id)
        config = node_data.get("config", {})
        expression = config.get("expression", "false")

        resolved_expr = resolve_templates(expression, context)
        if not isinstance(resolved_expr, str):
            resolved_expr = str(resolved_expr)

        await sr_mgr.create_item(
            run_id=str(run_id),
            step_id=node_id,
            step_type="condition",
            status="running",
            input={"expression": resolved_expr},
            attempt=1,
            started_at="now()",
        )
        await self._bus.emit(
            run_id,
            EventType.STEP_STARTED,
            step_id=node_id,
            payload={
                "step_id": node_id,
                "step_type": "condition",
                "step_label": node_data.get("label", node_id),
                "attempt": 1,
            },
        )

        step_start = time.monotonic()
        result = bool(safe_eval(resolved_expr, context))
        step_duration = int((time.monotonic() - step_start) * 1000)

        await sr_mgr.update_item(
            None,
            _filter={"run_id": str(run_id), "step_id": node_id, "attempt": 1},
            status="completed",
            output={"result": result, "branch": "true" if result else "false"},
            completed_at="now()",
        )
        await self._bus.emit(
            run_id,
            EventType.STEP_COMPLETED,
            step_id=node_id,
            payload={
                "step_id": node_id,
                "step_type": "condition",
                "status": "completed",
                "output_summary": {"result": result},
                "duration_ms": step_duration,
            },
        )

        # Skip the losing branch's exclusive subtree
        losing_branch = "false" if result else "true"
        skip_ids = graph.get_exclusive_branch_nodes(node_id, losing_branch)

        for skip_id in skip_ids:
            skip_type = graph.get_node_type(skip_id)
            await sr_mgr.create_item(
                run_id=str(run_id),
                step_id=skip_id,
                step_type=skip_type,
                status="skipped",
                attempt=1,
            )
            await self._bus.emit(
                run_id,
                EventType.STEP_SKIPPED,
                step_id=skip_id,
                payload={
                    "step_id": skip_id,
                    "status": "skipped",
                    "reason": f"Condition {node_id} evaluated to {result}",
                },
            )

        return {"result": result, "branch": "true" if result else "false"}

    # ------------------------------------------------------------------
    # Pause-type steps (approval, external event)
    # ------------------------------------------------------------------

    async def _handle_pause_step(
        self,
        run_id: UUID,
        node_id: str,
        step_type: str,
        step_label: str,
        config: dict[str, Any],
    ) -> dict[str, Any]:
        from app.db.models import step_run_manager_instance as sr_mgr

        waiting_for = "approval" if step_type == "wait_for_approval" else "event"
        reason = config.get("prompt", config.get("event_name", "Waiting"))

        await sr_mgr.create_item(
            run_id=str(run_id),
            step_id=node_id,
            step_type=step_type,
            status="waiting",
            input=config,
            attempt=1,
            started_at="now()",
        )
        await self._bus.emit(
            run_id,
            EventType.STEP_WAITING,
            step_id=node_id,
            payload={
                "step_id": node_id,
                "step_type": step_type,
                "status": "waiting",
                "waiting_for": waiting_for,
                "label": step_label,
            },
        )
        raise PauseExecution(
            step_id=node_id,
            reason=reason,
            pause_type=waiting_for,
        )

    # ------------------------------------------------------------------
    # for_each loop execution
    # ------------------------------------------------------------------

    async def _execute_for_each(
        self,
        run_id: UUID,
        node_id: str,
        config: dict[str, Any],
        context: dict[str, Any],
        graph: WorkflowGraph,
    ) -> dict[str, Any]:
        from app.db.models import step_run_manager_instance as sr_mgr

        node_data = graph.get_node_data(node_id)
        step_label = node_data.get("label", node_id)
        resolved_config = resolve_templates(config, context)

        items = resolved_config.get("items", [])
        if not isinstance(items, list):
            raise EngineError(f"for_each step {node_id}: 'items' must be a list")

        # The sub-step handler to run per item (if specified)
        sub_handler_type = resolved_config.get("handler", resolved_config.get("step_type"))
        sub_config_template = resolved_config.get("item_config", {})

        await sr_mgr.create_item(
            run_id=str(run_id),
            step_id=node_id,
            step_type="for_each",
            status="running",
            input={"item_count": len(items)},
            attempt=1,
            started_at="now()",
        )
        await self._bus.emit(
            run_id,
            EventType.STEP_STARTED,
            step_id=node_id,
            payload={
                "step_id": node_id,
                "step_type": "for_each",
                "step_label": step_label,
                "attempt": 1,
            },
        )

        step_start = time.monotonic()
        results: list[Any] = []
        max_parallel = resolved_config.get("max_parallel", 1)

        if sub_handler_type and sub_handler_type in STEP_REGISTRY:
            handler = STEP_REGISTRY[sub_handler_type]
            sem = asyncio.Semaphore(max_parallel)

            async def _run_item(idx: int, item: Any) -> dict[str, Any]:
                async with sem:
                    item_context = {**context, "_item": item, "_index": idx}
                    item_config = resolve_templates(sub_config_template, item_context)
                    return await handler.execute(item_config, item_context)

            tasks = [_run_item(i, item) for i, item in enumerate(items)]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Convert exceptions to error dicts
            processed: list[Any] = []
            for i, r in enumerate(results):
                if isinstance(r, Exception):
                    processed.append({"_error": str(r), "_index": i})
                else:
                    processed.append(r)
            results = processed
        else:
            # No sub-handler — just pass items through
            results = list(items)

        output = {
            "items": items,
            "count": len(items),
            "results": results,
        }

        step_duration = int((time.monotonic() - step_start) * 1000)
        await sr_mgr.update_item(
            None,
            _filter={"run_id": str(run_id), "step_id": node_id, "attempt": 1},
            status="completed",
            output=output,
            completed_at="now()",
        )
        await self._bus.emit(
            run_id,
            EventType.STEP_COMPLETED,
            step_id=node_id,
            payload={
                "step_id": node_id,
                "step_type": "for_each",
                "status": "completed",
                "output_summary": {
                    "count": len(items),
                    "results_count": len(results),
                },
                "duration_ms": step_duration,
            },
        )
        return output

    # ------------------------------------------------------------------
    # Cancellation check
    # ------------------------------------------------------------------

    async def _check_cancelled(
        self, run_id: UUID, active_tasks: list[asyncio.Task[Any]]
    ) -> None:
        from app.db.models import run_manager_instance as run_mgr

        fresh_run = await run_mgr.load_by_id(str(run_id))
        if fresh_run and fresh_run.status == "cancelled":
            for task in active_tasks:
                task.cancel()
            raise RunCancelled(f"Run {run_id} was cancelled")
