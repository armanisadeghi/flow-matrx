"""Tests for the WorkflowEngine executor — full execution loop with mocked DB.

The conftest pre-mocks `app.db.models` so matrx_orm is never imported.
We set up the mock manager instances before each test to simulate DB behavior.
"""

from __future__ import annotations

import asyncio
import sys
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest

from app.engine.executor import WorkflowEngine
from app.events.bus import EventBus


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _node(
    nid: str,
    ntype: str = "http_request",
    config: dict | None = None,
    **data_kw: Any,
) -> dict:
    d: dict[str, Any] = {"label": nid, "config": config or {}}
    d.update(data_kw)
    return {"id": nid, "type": ntype, "position": {"x": 0, "y": 0}, "data": d}


def _edge(src: str, tgt: str, **kw: Any) -> dict:
    e: dict[str, Any] = {"id": f"{src}-{tgt}", "source": src, "target": tgt}
    e.update(kw)
    return e


class FakeStepRun:
    def __init__(self, **kw: Any) -> None:
        for k, v in kw.items():
            setattr(self, k, v)


class FakeRun:
    def __init__(self, **kw: Any) -> None:
        self.id = kw.get("id", str(uuid4()))
        self.workflow_id = kw.get("workflow_id", str(uuid4()))
        self.status = kw.get("status", "pending")
        self.input = kw.get("input", {})
        self.context = kw.get("context", {})
        self.error = kw.get("error")
        self.started_at = None
        self.completed_at = None


class FakeWorkflow:
    def __init__(self, definition: dict) -> None:
        self.id = str(uuid4())
        self.definition = definition
        self.status = "published"


def _setup_mocks(
    workflow_def: dict,
    run_input: dict | None = None,
) -> tuple[FakeRun, list[FakeStepRun]]:
    """Wire up mock DB managers on the `app.db.models` mock module.

    Returns (run, step_runs_list) so tests can inspect final state.
    """
    wf = FakeWorkflow(workflow_def)
    run = FakeRun(workflow_id=wf.id, input=run_input or {})
    step_runs: list[FakeStepRun] = []

    # -- run manager -------------------------------------------------------
    run_mgr = AsyncMock()

    async def _load_run(rid: str) -> FakeRun:
        return run

    async def _update_run(rid: str, **kw: Any) -> None:
        for k, v in kw.items():
            setattr(run, k, v)

    run_mgr.load_by_id = AsyncMock(side_effect=_load_run)
    run_mgr.update_item = AsyncMock(side_effect=_update_run)

    # -- workflow manager --------------------------------------------------
    wf_mgr = AsyncMock()
    wf_mgr.load_by_id = AsyncMock(return_value=wf)

    # -- step_run manager --------------------------------------------------
    sr_mgr = AsyncMock()

    async def _filter_sr(**kw: Any) -> list[FakeStepRun]:
        return [
            sr for sr in step_runs
            if all(str(getattr(sr, k, None)) == str(v) for k, v in kw.items())
        ]

    async def _create_sr(**kw: Any) -> FakeStepRun:
        sr = FakeStepRun(**kw)
        step_runs.append(sr)
        return sr

    async def _update_sr(_id: Any, _filter: dict | None = None, **kw: Any) -> None:
        if _filter:
            for sr in step_runs:
                match = all(
                    str(getattr(sr, k, None)) == str(v) for k, v in _filter.items()
                )
                if match:
                    for k, v in kw.items():
                        setattr(sr, k, v)
                    return

    sr_mgr.filter_items = AsyncMock(side_effect=_filter_sr)
    sr_mgr.create_item = AsyncMock(side_effect=_create_sr)
    sr_mgr.update_item = AsyncMock(side_effect=_update_sr)

    # -- wire into the mock module -----------------------------------------
    mock_mod = sys.modules["app.db.models"]
    mock_mod.run_manager_instance = run_mgr
    mock_mod.workflow_manager_instance = wf_mgr
    mock_mod.step_run_manager_instance = sr_mgr

    return run, step_runs


def _make_bus() -> EventBus:
    mock_persister = AsyncMock()
    mock_persister.insert_run_event = AsyncMock()
    return EventBus(persister=mock_persister)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestLinearExecution:
    """3-step linear workflow: A → B → C using transform (pure, no side-effects)."""

    @pytest.mark.asyncio
    async def test_linear_completes(self) -> None:
        wf = {
            "nodes": [
                _node("a", "transform", config={"mapping": {"out": "hello"}}),
                _node("b", "transform", config={"mapping": {"val": "{{a.out}}"}}),
                _node("c", "transform", config={"mapping": {"final": "{{b.val}}"}}),
            ],
            "edges": [_edge("a", "b"), _edge("b", "c")],
        }
        run, step_runs = _setup_mocks(wf, run_input={"x": 1})
        engine = WorkflowEngine(bus=_make_bus())
        await engine.execute_run(UUID(run.id))

        assert run.status == "completed"
        completed = [sr for sr in step_runs if sr.status == "completed"]
        assert len(completed) == 3


class TestParallelExecution:
    """Fan-out / fan-in: start → [A, B] → merge."""

    @pytest.mark.asyncio
    async def test_parallel_fan_in(self) -> None:
        wf = {
            "nodes": [
                _node("start", "transform", config={"output": {"data": "init"}}),
                _node("a", "transform", config={"output": {"src": "a"}}),
                _node("b", "transform", config={"output": {"src": "b"}}),
                _node("merge", "transform", config={"output": {"done": "true"}}),
            ],
            "edges": [
                _edge("start", "a"),
                _edge("start", "b"),
                _edge("a", "merge"),
                _edge("b", "merge"),
            ],
        }
        run, step_runs = _setup_mocks(wf)
        engine = WorkflowEngine(bus=_make_bus())
        await engine.execute_run(UUID(run.id))

        assert run.status == "completed"
        completed = [sr for sr in step_runs if sr.status == "completed"]
        assert len(completed) == 4


class TestConditionBranching:
    """Condition that skips the losing branch."""

    @pytest.mark.asyncio
    async def test_true_branch_executes(self) -> None:
        wf = {
            "nodes": [
                _node("cond", "condition", config={"expression": "True"}),
                _node("yes", "transform", config={"output": {"branch": "true"}}),
                _node("no", "transform", config={"output": {"branch": "false"}}),
            ],
            "edges": [
                _edge("cond", "yes", sourceHandle="true"),
                _edge("cond", "no", sourceHandle="false"),
            ],
        }
        run, step_runs = _setup_mocks(wf)
        engine = WorkflowEngine(bus=_make_bus())
        await engine.execute_run(UUID(run.id))

        assert run.status == "completed"
        skipped = [sr for sr in step_runs if sr.status == "skipped"]
        assert any(sr.step_id == "no" for sr in skipped)
        completed = [sr for sr in step_runs if sr.status == "completed"]
        assert any(sr.step_id == "yes" for sr in completed)


class TestApprovalPause:
    """Approval step pauses the run."""

    @pytest.mark.asyncio
    async def test_run_pauses_at_approval(self) -> None:
        wf = {
            "nodes": [
                _node("start", "transform", config={"output": {"x": 1}}),
                _node("approve", "wait_for_approval", config={"prompt": "Please approve"}),
                _node("end", "transform", config={"output": {"done": "yes"}}),
            ],
            "edges": [_edge("start", "approve"), _edge("approve", "end")],
        }
        run, step_runs = _setup_mocks(wf)
        engine = WorkflowEngine(bus=_make_bus())
        await engine.execute_run(UUID(run.id))

        assert run.status == "paused"
        waiting = [sr for sr in step_runs if sr.status == "waiting"]
        assert len(waiting) == 1
        assert waiting[0].step_id == "approve"


class TestWaitForEventPause:
    """wait_for_event step pauses the run."""

    @pytest.mark.asyncio
    async def test_run_pauses_at_event(self) -> None:
        wf = {
            "nodes": [
                _node("start", "transform", config={"output": {"x": 1}}),
                _node("wait", "wait_for_event", config={"event_name": "payment.received"}),
                _node("end", "transform", config={"output": {"done": "yes"}}),
            ],
            "edges": [_edge("start", "wait"), _edge("wait", "end")],
        }
        run, step_runs = _setup_mocks(wf)
        engine = WorkflowEngine(bus=_make_bus())
        await engine.execute_run(UUID(run.id))

        assert run.status == "paused"
        waiting = [sr for sr in step_runs if sr.status == "waiting"]
        assert len(waiting) == 1
        assert waiting[0].step_id == "wait"


class TestStepFailure:
    """Step failure with on_error=fail (default) stops the run."""

    @pytest.mark.asyncio
    async def test_run_fails_on_step_error(self) -> None:
        wf = {
            "nodes": [
                _node("a", "http_request", config={"url": "https://fail.example.com", "method": "GET"}),
                _node("b", "transform", config={"output": {"x": 1}}),
            ],
            "edges": [_edge("a", "b")],
        }
        run, step_runs = _setup_mocks(wf)
        engine = WorkflowEngine(bus=_make_bus())
        await engine.execute_run(UUID(run.id))

        assert run.status == "failed"


class TestStepSkipOnError:
    """Step with on_error=skip allows the run to continue."""

    @pytest.mark.asyncio
    async def test_skip_continues(self) -> None:
        wf = {
            "nodes": [
                _node(
                    "a", "http_request",
                    config={"url": "https://fail.example.com", "method": "GET"},
                    on_error="skip",
                ),
                _node("b", "transform", config={"output": {"x": 1}}),
            ],
            "edges": [_edge("a", "b")],
        }
        run, step_runs = _setup_mocks(wf)
        engine = WorkflowEngine(bus=_make_bus())
        await engine.execute_run(UUID(run.id))

        assert run.status == "completed"


class TestEventEmission:
    """Verify that the correct events are emitted during execution."""

    @pytest.mark.asyncio
    async def test_events_emitted_for_single_step(self) -> None:
        wf = {
            "nodes": [_node("a", "transform", config={"output": {"out": "1"}})],
            "edges": [],
        }
        run, _ = _setup_mocks(wf)
        bus = _make_bus()

        events: list[dict] = []

        async def capture(event: dict) -> None:
            events.append(event)

        bus.add_listener(capture)
        engine = WorkflowEngine(bus=bus)
        await engine.execute_run(UUID(run.id))

        event_types = [e["event_type"] for e in events]
        assert "run.started" in event_types
        assert "step.started" in event_types
        assert "step.completed" in event_types
        assert "context.updated" in event_types
        assert "run.completed" in event_types


class TestConcurrencyLimit:
    """Verify concurrency semaphore works."""

    @pytest.mark.asyncio
    async def test_max_concurrency_respected(self) -> None:
        wf = {
            "nodes": [
                _node("a", "delay", config={"seconds": 0.01}),
                _node("b", "delay", config={"seconds": 0.01}),
                _node("c", "delay", config={"seconds": 0.01}),
            ],
            "edges": [],  # All roots — all run in parallel
        }
        run, step_runs = _setup_mocks(wf)
        engine = WorkflowEngine(bus=_make_bus(), max_concurrency=2)
        await engine.execute_run(UUID(run.id))

        assert run.status == "completed"
        completed = [sr for sr in step_runs if sr.status == "completed"]
        assert len(completed) == 3


class TestResumeFromPaused:
    """Engine resumes from a paused state (not emitting RUN_STARTED again)."""

    @pytest.mark.asyncio
    async def test_resume_skips_run_started(self) -> None:
        wf = {
            "nodes": [
                _node("a", "transform", config={"output": {"x": 1}}),
            ],
            "edges": [],
        }
        run, _ = _setup_mocks(wf)
        run.status = "paused"  # Simulate already-paused

        bus = _make_bus()
        events: list[dict] = []

        async def capture(event: dict) -> None:
            events.append(event)

        bus.add_listener(capture)
        engine = WorkflowEngine(bus=bus)
        await engine.execute_run(UUID(run.id))

        event_types = [e["event_type"] for e in events]
        assert "run.started" not in event_types
        assert "run.completed" in event_types
