from __future__ import annotations

import pytest

from app.validation.workflow import validate_workflow


def _make_node(nid: str, ntype: str = "http_request") -> dict:
    return {"id": nid, "type": ntype, "data": {"label": nid, "config": {}}}


def _make_edge(source: str, target: str, **kwargs: object) -> dict:
    edge = {"id": f"{source}-{target}", "source": source, "target": target}
    edge.update(kwargs)
    return edge


class TestValidateWorkflow:
    def test_empty_nodes_error(self):
        errors = validate_workflow({"nodes": [], "edges": []})
        assert any("at least one node" in e for e in errors)

    def test_valid_linear_workflow(self):
        definition = {
            "nodes": [_make_node("a"), _make_node("b")],
            "edges": [_make_edge("a", "b")],
        }
        errors = validate_workflow(definition)
        assert errors == []

    def test_dangling_edge_source(self):
        definition = {
            "nodes": [_make_node("a")],
            "edges": [_make_edge("ghost", "a")],
        }
        errors = validate_workflow(definition)
        assert any("ghost" in e for e in errors)

    def test_dangling_edge_target(self):
        definition = {
            "nodes": [_make_node("a")],
            "edges": [_make_edge("a", "ghost")],
        }
        errors = validate_workflow(definition)
        assert any("ghost" in e for e in errors)

    def test_cycle_detection(self):
        definition = {
            "nodes": [_make_node("a"), _make_node("b")],
            "edges": [_make_edge("a", "b"), _make_edge("b", "a")],
        }
        errors = validate_workflow(definition)
        assert any("cycle" in e.lower() for e in errors)

    def test_orphan_detection(self):
        definition = {
            "nodes": [_make_node("a"), _make_node("b"), _make_node("orphan")],
            "edges": [_make_edge("a", "b")],
        }
        errors = validate_workflow(definition)
        assert any("orphan" in e.lower() for e in errors)

    def test_unregistered_step_type(self):
        definition = {
            "nodes": [{"id": "a", "type": "nonexistent_type", "data": {"config": {}}}],
            "edges": [],
        }
        errors = validate_workflow(definition)
        assert any("unregistered" in e.lower() for e in errors)

    def test_condition_engine_handled_type_accepted(self):
        definition = {
            "nodes": [
                _make_node("start"),
                {"id": "cond", "type": "condition", "data": {"config": {"expression": "true"}}},
                _make_node("yes"),
                _make_node("no"),
            ],
            "edges": [
                _make_edge("start", "cond"),
                _make_edge("cond", "yes", sourceHandle="true"),
                _make_edge("cond", "no", sourceHandle="false"),
            ],
        }
        errors = validate_workflow(definition)
        unregistered = [e for e in errors if "unregistered" in e.lower()]
        assert unregistered == []

    def test_wait_for_approval_engine_handled_type_accepted(self):
        definition = {
            "nodes": [
                _make_node("start"),
                {"id": "approval", "type": "wait_for_approval", "data": {"config": {}}},
            ],
            "edges": [_make_edge("start", "approval")],
        }
        errors = validate_workflow(definition)
        unregistered = [e for e in errors if "unregistered" in e.lower()]
        assert unregistered == []

    def test_condition_missing_true_branch(self):
        definition = {
            "nodes": [
                {"id": "cond", "type": "condition", "data": {"config": {}}},
                _make_node("no"),
            ],
            "edges": [_make_edge("cond", "no", sourceHandle="false")],
        }
        errors = validate_workflow(definition)
        assert any("missing 'true'" in e for e in errors)

    def test_condition_missing_false_branch(self):
        definition = {
            "nodes": [
                {"id": "cond", "type": "condition", "data": {"config": {}}},
                _make_node("yes"),
            ],
            "edges": [_make_edge("cond", "yes", sourceHandle="true")],
        }
        errors = validate_workflow(definition)
        assert any("missing 'false'" in e for e in errors)

    def test_condition_edge_data_condition_format(self):
        definition = {
            "nodes": [
                _make_node("start"),
                {"id": "cond", "type": "condition", "data": {"config": {"expression": "true"}}},
                _make_node("yes"),
                _make_node("no"),
            ],
            "edges": [
                _make_edge("start", "cond"),
                _make_edge("cond", "yes", data={"condition": "true"}),
                _make_edge("cond", "no", data={"condition": "false"}),
            ],
        }
        errors = validate_workflow(definition)
        condition_errors = [e for e in errors if "missing" in e and ("true" in e or "false" in e)]
        assert condition_errors == []

    def test_template_ref_to_input_is_valid(self):
        definition = {
            "nodes": [
                {"id": "a", "type": "http_request", "data": {
                    "config": {"url": "{{input.endpoint}}"},
                }},
            ],
            "edges": [],
        }
        errors = validate_workflow(definition)
        ref_errors = [e for e in errors if "references" in e and "not an upstream" in e]
        assert ref_errors == []

    def test_template_ref_to_nonexistent_upstream_fails(self):
        definition = {
            "nodes": [
                _make_node("a"),
                {"id": "b", "type": "http_request", "data": {
                    "config": {"url": "{{nonexistent_step.url}}"},
                }},
            ],
            "edges": [_make_edge("a", "b")],
        }
        errors = validate_workflow(definition)
        assert any("nonexistent_step" in e for e in errors)

    def test_template_ref_to_actual_upstream_is_valid(self):
        definition = {
            "nodes": [
                _make_node("a"),
                {"id": "b", "type": "http_request", "data": {
                    "config": {"url": "{{a.result.url}}"},
                }},
            ],
            "edges": [_make_edge("a", "b")],
        }
        errors = validate_workflow(definition)
        ref_errors = [e for e in errors if "references" in e and "not an upstream" in e]
        assert ref_errors == []
