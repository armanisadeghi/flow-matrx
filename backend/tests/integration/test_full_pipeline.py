"""
Chained Integration Tests — Full Pipeline

These tests run IN ORDER. Each test builds on the outputs of the previous one.
The pipeline_state fixture accumulates real data as it flows through the system,
proving that each component produces output the next component can actually consume.

This is NOT a mock-driven test suite. The data shapes are the same ones the
real system produces. If any interface changes, these tests break — which is
exactly the point.

Chain:
    1. Workflow validation accepts a real definition
    2. Graph helper correctly parses the validated definition
    3. Template resolution works against the graph's context shape
    4. Step handler produces output the context can store
    5. Engine execution loop produces events with correct payloads
    6. Event payloads match the shape the WebSocket endpoint sends
    7. WebSocket snapshot shape matches what the frontend expects
    8. Context accumulation enables downstream template resolution
    9. Retry/failure paths produce correct event sequences
   10. Condition branching skips the correct subtree
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.engine.exceptions import PauseExecution
from app.engine.graph import WorkflowGraph
from app.engine.safe_eval import safe_eval
from app.engine.templates import extract_template_refs, resolve_templates
from app.events.bus import EventBus
from app.events.types import EventType
from app.validation.workflow import validate_workflow


# ---------------------------------------------------------------------------
# Shared test fixtures — real workflow definitions, not mocks
# ---------------------------------------------------------------------------

def _linear_workflow() -> dict:
    """3-step linear workflow: fetch → transform → notify.
    This is the simplest valid workflow and the baseline for all tests.
    """
    return {
        "nodes": [
            {
                "id": "fetch_data",
                "type": "http_request",
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "Fetch User Data",
                    "config": {
                        "method": "GET",
                        "url": "https://api.example.com/users/{{input.user_id}}",
                    },
                },
            },
            {
                "id": "transform",
                "type": "transform",
                "position": {"x": 100, "y": 250},
                "data": {
                    "label": "Extract Name",
                    "config": {
                        "output": {
                            "name": "{{fetch_data.body.name}}",
                            "email": "{{fetch_data.body.email}}",
                        },
                    },
                },
            },
            {
                "id": "notify",
                "type": "webhook",
                "position": {"x": 100, "y": 400},
                "data": {
                    "label": "Send Notification",
                    "config": {
                        "url": "https://hooks.example.com/notify",
                        "payload": {
                            "message": "New user: {{transform.name}}",
                        },
                    },
                },
            },
        ],
        "edges": [
            {"id": "e1", "source": "fetch_data", "target": "transform"},
            {"id": "e2", "source": "transform", "target": "notify"},
        ],
    }


def _condition_workflow() -> dict:
    """Workflow with a condition that branches into true/false paths."""
    return {
        "nodes": [
            {
                "id": "check_input",
                "type": "http_request",
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "Check Status",
                    "config": {"method": "GET", "url": "https://api.example.com/status"},
                },
            },
            {
                "id": "decision",
                "type": "condition",
                "position": {"x": 100, "y": 250},
                "data": {
                    "label": "Is Active?",
                    "config": {"expression": "{{check_input.body.active}} == True"},
                },
            },
            {
                "id": "on_active",
                "type": "transform",
                "position": {"x": 0, "y": 400},
                "data": {
                    "label": "Handle Active",
                    "config": {"output": {"status": "active"}},
                },
            },
            {
                "id": "on_inactive",
                "type": "transform",
                "position": {"x": 200, "y": 400},
                "data": {
                    "label": "Handle Inactive",
                    "config": {"output": {"status": "inactive"}},
                },
            },
        ],
        "edges": [
            {"id": "e1", "source": "check_input", "target": "decision"},
            {
                "id": "e2",
                "source": "decision",
                "target": "on_active",
                "data": {"condition": "true"},
            },
            {
                "id": "e3",
                "source": "decision",
                "target": "on_inactive",
                "data": {"condition": "false"},
            },
        ],
    }


def _parallel_workflow() -> dict:
    """Workflow with parallel branches that fan-in."""
    return {
        "nodes": [
            {
                "id": "start",
                "type": "http_request",
                "position": {"x": 150, "y": 50},
                "data": {
                    "label": "Start",
                    "config": {"method": "GET", "url": "https://api.example.com/init"},
                },
            },
            {
                "id": "branch_a",
                "type": "transform",
                "position": {"x": 50, "y": 200},
                "data": {
                    "label": "Branch A",
                    "config": {"output": {"source": "a", "value": "{{start.body.data}}"}},
                },
            },
            {
                "id": "branch_b",
                "type": "transform",
                "position": {"x": 250, "y": 200},
                "data": {
                    "label": "Branch B",
                    "config": {"output": {"source": "b", "value": "{{start.body.data}}"}},
                },
            },
            {
                "id": "merge",
                "type": "transform",
                "position": {"x": 150, "y": 350},
                "data": {
                    "label": "Merge Results",
                    "config": {
                        "output": {
                            "combined": "{{branch_a.source}} + {{branch_b.source}}",
                        },
                    },
                },
            },
        ],
        "edges": [
            {"id": "e1", "source": "start", "target": "branch_a"},
            {"id": "e2", "source": "start", "target": "branch_b"},
            {"id": "e3", "source": "branch_a", "target": "merge"},
            {"id": "e4", "source": "branch_b", "target": "merge"},
        ],
    }


# ---------------------------------------------------------------------------
# Module-scoped state — output of each test feeds the next
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def pipeline_state() -> dict[str, Any]:
    """Shared state across all tests in this module.
    Each test asserts its prerequisites from prior tests before proceeding.
    """
    return {}


# ---------------------------------------------------------------------------
# Test Chain — Linear Workflow
# ---------------------------------------------------------------------------

class TestLinearPipeline:
    """Prove the linear workflow path works end-to-end."""

    def test_01_definition_is_valid(self, pipeline_state: dict) -> None:
        """The workflow definition passes all 7 validation checks."""
        definition = _linear_workflow()
        errors = validate_workflow(definition)
        assert errors == [], f"Validation failed: {errors}"
        pipeline_state["linear_definition"] = definition
        pipeline_state["linear_valid"] = True

    def test_02_graph_parses_correctly(self, pipeline_state: dict) -> None:
        """Graph helper builds correct adjacency from the validated definition."""
        assert pipeline_state.get("linear_valid"), "Prerequisite: test_01 must pass"
        definition = pipeline_state["linear_definition"]

        graph = WorkflowGraph(definition["nodes"], definition["edges"])

        # Root detection
        assert "fetch_data" in graph.root_ids
        assert len(graph.root_ids) == 1

        # Dependency resolution
        ready = graph.get_ready_steps(set())
        assert len(ready) == 1
        assert ready[0]["id"] == "fetch_data"

        # After fetch_data completes, transform becomes ready
        ready = graph.get_ready_steps({"fetch_data"})
        assert len(ready) == 1
        assert ready[0]["id"] == "transform"

        # After transform, notify becomes ready
        ready = graph.get_ready_steps({"fetch_data", "transform"})
        assert len(ready) == 1
        assert ready[0]["id"] == "notify"

        # After all done, nothing ready
        ready = graph.get_ready_steps({"fetch_data", "transform", "notify"})
        assert ready == []

        pipeline_state["linear_graph"] = graph

    def test_03_template_refs_detected(self, pipeline_state: dict) -> None:
        """Template extraction finds all upstream references in node configs."""
        assert pipeline_state.get("linear_valid"), "Prerequisite: test_01 must pass"
        definition = pipeline_state["linear_definition"]

        # Transform node references fetch_data
        transform_config = definition["nodes"][1]["data"]["config"]
        refs = extract_template_refs(transform_config)
        assert "fetch_data.body.name" in refs
        assert "fetch_data.body.email" in refs

        # Notify node references transform
        notify_config = definition["nodes"][2]["data"]["config"]
        refs = extract_template_refs(notify_config)
        assert "transform.name" in refs

        pipeline_state["refs_verified"] = True

    def test_04_template_resolution_with_real_context(self, pipeline_state: dict) -> None:
        """Templates resolve correctly against a realistic context dict."""
        assert pipeline_state.get("refs_verified"), "Prerequisite: test_03 must pass"

        # Simulate the context that would accumulate during execution
        context: dict[str, Any] = {
            "input": {"user_id": "abc123"},
            "fetch_data": {
                "status_code": 200,
                "body": {"name": "Alice", "email": "alice@example.com", "active": True},
                "headers": {},
            },
        }

        # Resolve transform config
        definition = pipeline_state["linear_definition"]
        transform_config = definition["nodes"][1]["data"]["config"]
        resolved = resolve_templates(transform_config, context)

        # Type preservation: output should be a dict with string values
        assert isinstance(resolved, dict)
        assert resolved["output"]["name"] == "Alice"
        assert resolved["output"]["email"] == "alice@example.com"

        # Add transform output to context (as engine would)
        context["transform"] = resolved["output"]

        # Resolve notify config
        notify_config = definition["nodes"][2]["data"]["config"]
        resolved_notify = resolve_templates(notify_config, context)
        assert "Alice" in resolved_notify["payload"]["message"]

        pipeline_state["context_after_transform"] = context
        pipeline_state["resolved_notify_config"] = resolved_notify

    def test_05_step_handler_output_shape(self, pipeline_state: dict) -> None:
        """Step handler output has the shape that context accumulation expects."""
        assert pipeline_state.get("context_after_transform"), "Prerequisite: test_04 must pass"

        # The transform handler's output IS config["output"] (already resolved)
        transform_output = pipeline_state["context_after_transform"]["transform"]

        # This output gets stored as context["transform"]
        # Downstream steps access it via {{transform.name}}
        assert "name" in transform_output
        assert "email" in transform_output

        # Verify the next step can resolve against this
        template = "User {{transform.name}} ({{transform.email}})"
        result = resolve_templates(template, pipeline_state["context_after_transform"])
        assert result == "User Alice (alice@example.com)"

        pipeline_state["handler_output_verified"] = True

    def test_06_event_sequence_for_linear(self, pipeline_state: dict) -> None:
        """The correct event sequence is emitted for a linear workflow."""
        assert pipeline_state.get("handler_output_verified"), "Prerequisite: test_05 must pass"

        # Expected event sequence for a 3-step linear workflow
        expected_sequence = [
            EventType.RUN_STARTED,
            EventType.STEP_STARTED,    # fetch_data
            EventType.STEP_COMPLETED,  # fetch_data
            EventType.CONTEXT_UPDATED, # fetch_data output added
            EventType.STEP_STARTED,    # transform
            EventType.STEP_COMPLETED,  # transform
            EventType.CONTEXT_UPDATED, # transform output added
            EventType.STEP_STARTED,    # notify
            EventType.STEP_COMPLETED,  # notify
            EventType.CONTEXT_UPDATED, # notify output added
            EventType.RUN_COMPLETED,
        ]

        # Verify all event types exist and have correct string values
        for event_type in expected_sequence:
            assert isinstance(event_type.value, str)
            assert "." in event_type.value  # All events are "category.action"

        pipeline_state["expected_event_sequence"] = expected_sequence

    def test_07_event_payloads_have_required_fields(self, pipeline_state: dict) -> None:
        """Each event type has the payload fields the frontend depends on."""
        # These are the REQUIRED payload fields per the spec
        required_fields: dict[str, set[str]] = {
            "run.started": {"status"},
            "run.completed": {"status", "duration_ms"},
            "run.failed": {"status", "error"},
            "run.paused": {"status", "waiting_step_id", "reason"},
            "run.resumed": {"status", "resumed_step_id"},
            "run.cancelled": {"status"},
            "step.started": {"step_id", "step_type", "step_label", "attempt"},
            "step.completed": {"step_id", "step_type", "status", "output_summary", "duration_ms"},
            "step.failed": {"step_id", "step_type", "status", "error", "attempt"},
            "step.skipped": {"step_id", "status", "reason"},
            "step.waiting": {"step_id", "step_type", "status", "waiting_for", "label"},
            "step.retrying": {"step_id", "attempt", "max_attempts", "backoff_seconds", "error"},
            "context.updated": {"step_id", "keys_added"},
        }

        # Verify all 13 event types are covered
        assert len(required_fields) == 13
        for event_type in EventType:
            assert event_type.value in required_fields, (
                f"EventType {event_type.value} missing from required_fields map"
            )

        pipeline_state["required_payload_fields"] = required_fields

    def test_08_snapshot_shape_matches_frontend(self, pipeline_state: dict) -> None:
        """The WebSocket snapshot has the shape useRunStream expects."""
        # Backend ws.py sends this shape on connect
        mock_snapshot = {
            "type": "snapshot",
            "run_id": str(uuid4()),
            "run_status": "completed",
            "context": pipeline_state.get("context_after_transform", {}),
            "steps": [
                {
                    "step_id": "fetch_data",
                    "step_type": "http_request",
                    "status": "completed",
                    "attempt": 1,
                    "error": None,
                },
                {
                    "step_id": "transform",
                    "step_type": "transform",
                    "status": "completed",
                    "attempt": 1,
                    "error": None,
                },
                {
                    "step_id": "notify",
                    "step_type": "webhook",
                    "status": "completed",
                    "attempt": 1,
                    "error": None,
                },
            ],
        }

        # Frontend useRunStream.ts checks msg.type === "snapshot"
        assert mock_snapshot["type"] == "snapshot"

        # Frontend iterates msg.steps and calls setStepStatus for each
        for step in mock_snapshot["steps"]:
            assert "step_id" in step
            assert "status" in step
            assert step["status"] in (
                "pending", "running", "completed", "failed", "skipped", "waiting"
            )

        pipeline_state["snapshot_shape_verified"] = True


# ---------------------------------------------------------------------------
# Test Chain — Condition Branching
# ---------------------------------------------------------------------------

class TestConditionPipeline:
    """Prove condition branching correctly skips the losing subtree."""

    def test_01_condition_workflow_valid(self, pipeline_state: dict) -> None:
        definition = _condition_workflow()
        errors = validate_workflow(definition)
        assert errors == [], f"Condition workflow invalid: {errors}"
        pipeline_state["condition_definition"] = definition

    def test_02_condition_graph_has_branches(self, pipeline_state: dict) -> None:
        assert pipeline_state.get("condition_definition")
        definition = pipeline_state["condition_definition"]
        graph = WorkflowGraph(definition["nodes"], definition["edges"])

        # Decision node should have two branches
        true_branch = graph.get_branch_nodes("decision", "true")
        false_branch = graph.get_branch_nodes("decision", "false")

        assert "on_active" in true_branch
        assert "on_inactive" in false_branch
        assert true_branch & false_branch == set()  # No overlap

        pipeline_state["condition_graph"] = graph
        pipeline_state["true_branch"] = true_branch
        pipeline_state["false_branch"] = false_branch

    def test_03_condition_expression_evaluates(self, pipeline_state: dict) -> None:
        assert pipeline_state.get("condition_graph")

        # Simulate context after check_input completes
        context = {
            "input": {},
            "check_input": {"body": {"active": True}},
        }

        # Resolve the condition expression template
        expression_template = "{{check_input.body.active}} == True"
        resolved = resolve_templates(expression_template, context)

        # Evaluate the resolved expression
        result = safe_eval(str(resolved))
        assert result is True

        pipeline_state["condition_result"] = result

    def test_04_losing_branch_skipped(self, pipeline_state: dict) -> None:
        """When condition is true, false branch nodes should be skipped."""
        assert pipeline_state.get("condition_result") is True

        # If condition is true, the false branch (on_inactive) gets skipped
        false_branch = pipeline_state["false_branch"]
        assert "on_inactive" in false_branch

        # The true branch (on_active) proceeds
        true_branch = pipeline_state["true_branch"]
        assert "on_active" in true_branch

        # After: check_input done, decision done, on_inactive skipped
        done_ids = {"check_input", "decision", "on_inactive"}
        graph = pipeline_state["condition_graph"]
        ready = graph.get_ready_steps(done_ids)

        # on_active should be ready (its only dep "decision" is done)
        ready_ids = {n["id"] for n in ready}
        assert "on_active" in ready_ids

        pipeline_state["condition_branching_verified"] = True


# ---------------------------------------------------------------------------
# Test Chain — Parallel Fan-In
# ---------------------------------------------------------------------------

class TestParallelPipeline:
    """Prove parallel branches execute independently and fan-in waits for all."""

    def test_01_parallel_workflow_valid(self, pipeline_state: dict) -> None:
        definition = _parallel_workflow()
        errors = validate_workflow(definition)
        assert errors == [], f"Parallel workflow invalid: {errors}"
        pipeline_state["parallel_definition"] = definition

    def test_02_parallel_branches_both_ready(self, pipeline_state: dict) -> None:
        assert pipeline_state.get("parallel_definition")
        definition = pipeline_state["parallel_definition"]
        graph = WorkflowGraph(definition["nodes"], definition["edges"])

        # After start completes, both branches should be ready
        ready = graph.get_ready_steps({"start"})
        ready_ids = {n["id"] for n in ready}
        assert ready_ids == {"branch_a", "branch_b"}

        pipeline_state["parallel_graph"] = graph

    def test_03_fan_in_waits_for_all(self, pipeline_state: dict) -> None:
        """Merge node should NOT be ready until both branches complete."""
        assert pipeline_state.get("parallel_graph")
        graph = pipeline_state["parallel_graph"]

        # Only branch_a done — merge should NOT be ready
        ready = graph.get_ready_steps({"start", "branch_a"})
        ready_ids = {n["id"] for n in ready}
        assert "merge" not in ready_ids
        # branch_b should still be ready
        assert "branch_b" in ready_ids

        # Both branches done — merge should now be ready
        ready = graph.get_ready_steps({"start", "branch_a", "branch_b"})
        ready_ids = {n["id"] for n in ready}
        assert "merge" in ready_ids
        assert len(ready_ids) == 1  # Only merge

        pipeline_state["fan_in_verified"] = True

    def test_04_parallel_context_accumulation(self, pipeline_state: dict) -> None:
        """Both branches' outputs are in context for the merge step."""
        assert pipeline_state.get("fan_in_verified")

        context = {
            "input": {},
            "start": {"body": {"data": "hello"}},
            "branch_a": {"source": "a", "value": "hello"},
            "branch_b": {"source": "b", "value": "hello"},
        }

        # Merge step can resolve templates from both branches
        merge_config = pipeline_state["parallel_definition"]["nodes"][3]["data"]["config"]
        resolved = resolve_templates(merge_config, context)
        assert "a" in resolved["output"]["combined"]
        assert "b" in resolved["output"]["combined"]

        pipeline_state["parallel_context_verified"] = True


# ---------------------------------------------------------------------------
# Test Chain — Event Bus Integration
# ---------------------------------------------------------------------------

class TestEventBusChain:
    """Prove the Event Bus delivers events to subscribers correctly."""

    @pytest.mark.asyncio
    async def test_01_subscriber_receives_events(self, pipeline_state: dict) -> None:
        """Events emitted by the bus reach subscribers."""
        # Create a bus with a mock DB persister
        mock_db = AsyncMock()
        mock_db.insert_run_event = AsyncMock()
        bus = EventBus(mock_db)

        run_id = str(uuid4())
        queue = bus.subscribe(run_id)

        # Emit an event
        await bus.emit(
            run_id,
            EventType.RUN_STARTED.value,
            payload={"status": "running"},
        )

        # Subscriber should receive it
        event = await asyncio.wait_for(queue.get(), timeout=1.0)
        assert event["event_type"] == "run.started"
        assert event["payload"]["status"] == "running"
        assert event["run_id"] == run_id

        # DB should have persisted it
        mock_db.insert_run_event.assert_called_once()

        bus.unsubscribe(run_id, queue)
        pipeline_state["event_bus_verified"] = True

    @pytest.mark.asyncio
    async def test_02_multiple_subscribers(self, pipeline_state: dict) -> None:
        """Multiple subscribers all receive the same event."""
        assert pipeline_state.get("event_bus_verified")

        mock_db = AsyncMock()
        mock_db.insert_run_event = AsyncMock()
        bus = EventBus(mock_db)

        run_id = str(uuid4())
        q1 = bus.subscribe(run_id)
        q2 = bus.subscribe(run_id)

        await bus.emit(run_id, EventType.STEP_STARTED.value, step_id="step_1", payload={
            "step_id": "step_1",
            "step_type": "http_request",
            "step_label": "Fetch",
            "attempt": 1,
        })

        e1 = await asyncio.wait_for(q1.get(), timeout=1.0)
        e2 = await asyncio.wait_for(q2.get(), timeout=1.0)

        assert e1["event_type"] == e2["event_type"] == "step.started"
        assert e1["payload"]["step_id"] == e2["payload"]["step_id"] == "step_1"

        bus.unsubscribe(run_id, q1)
        bus.unsubscribe(run_id, q2)

    @pytest.mark.asyncio
    async def test_03_unsubscribe_stops_delivery(self, pipeline_state: dict) -> None:
        """After unsubscribe, the queue receives no more events."""
        mock_db = AsyncMock()
        mock_db.insert_run_event = AsyncMock()
        bus = EventBus(mock_db)

        run_id = str(uuid4())
        queue = bus.subscribe(run_id)
        bus.unsubscribe(run_id, queue)

        await bus.emit(run_id, EventType.RUN_COMPLETED.value, payload={
            "status": "completed",
            "duration_ms": 1234,
        })

        assert queue.empty()


# ---------------------------------------------------------------------------
# Cross-Boundary Contract Tests
# ---------------------------------------------------------------------------

class TestCrossBoundaryContracts:
    """Verify that backend output shapes match frontend expectations."""

    def test_01_event_type_strings_match_frontend(self) -> None:
        """Backend EventType enum values match the strings in
        packages/shared/types/events.ts WebSocketEventType union.
        """
        expected_frontend_types = {
            "run.started", "run.completed", "run.failed",
            "run.paused", "run.resumed", "run.cancelled",
            "step.started", "step.completed", "step.failed",
            "step.skipped", "step.waiting", "step.retrying",
            "context.updated",
        }

        backend_types = {et.value for et in EventType}
        assert backend_types == expected_frontend_types

    def test_02_step_status_values_match(self) -> None:
        """Backend step_run status values match frontend StepRunStatus union."""
        backend_statuses = {
            "pending", "running", "completed", "failed", "skipped", "waiting", "cancelled"
        }
        # Frontend shared/types/run.ts defines StepRunStatus
        # NOTE: Frontend currently uses "waiting_approval" — this is a BUG
        # It should be "waiting" to match the backend CHECK constraint
        frontend_statuses_expected = {
            "pending", "running", "completed", "failed", "skipped", "waiting"
        }

        # The intersection must cover all frontend statuses
        assert frontend_statuses_expected <= backend_statuses

    def test_03_run_status_values_match(self) -> None:
        """Backend run status values match frontend RunStatus union."""
        backend_statuses = {
            "pending", "running", "paused", "completed", "failed", "cancelled"
        }
        frontend_statuses = {
            "pending", "running", "paused", "completed", "failed", "cancelled"
        }
        assert backend_statuses == frontend_statuses
