from __future__ import annotations

import pytest

from app.engine.graph import WorkflowGraph


def _make_node(nid: str, ntype: str = "http_request") -> dict:
    return {"id": nid, "type": ntype, "data": {"label": nid, "config": {}}}


def _make_edge(source: str, target: str, **kwargs: object) -> dict:
    edge = {"id": f"{source}-{target}", "source": source, "target": target}
    edge.update(kwargs)
    return edge


class TestWorkflowGraphBasic:
    def test_single_node(self):
        graph = WorkflowGraph([_make_node("a")], [])
        assert graph.root_ids == ["a"]
        assert graph.node_ids == {"a"}

    def test_linear_chain(self):
        nodes = [_make_node("a"), _make_node("b"), _make_node("c")]
        edges = [_make_edge("a", "b"), _make_edge("b", "c")]
        graph = WorkflowGraph(nodes, edges)

        assert graph.root_ids == ["a"]
        assert graph.get_downstream("a") == ["b"]
        assert graph.get_downstream("b") == ["c"]
        assert graph.get_downstream("c") == []


class TestReadySteps:
    def test_root_always_ready(self):
        nodes = [_make_node("a"), _make_node("b")]
        edges = [_make_edge("a", "b")]
        graph = WorkflowGraph(nodes, edges)

        ready = graph.get_ready_steps(set())
        assert len(ready) == 1
        assert ready[0]["id"] == "a"

    def test_child_ready_after_parent(self):
        nodes = [_make_node("a"), _make_node("b")]
        edges = [_make_edge("a", "b")]
        graph = WorkflowGraph(nodes, edges)

        ready = graph.get_ready_steps({"a"})
        assert len(ready) == 1
        assert ready[0]["id"] == "b"

    def test_parallel_roots(self):
        nodes = [_make_node("a"), _make_node("b"), _make_node("c")]
        edges = [_make_edge("a", "c"), _make_edge("b", "c")]
        graph = WorkflowGraph(nodes, edges)

        ready = graph.get_ready_steps(set())
        ids = {n["id"] for n in ready}
        assert ids == {"a", "b"}

    def test_join_needs_all_parents(self):
        nodes = [_make_node("a"), _make_node("b"), _make_node("c")]
        edges = [_make_edge("a", "c"), _make_edge("b", "c")]
        graph = WorkflowGraph(nodes, edges)

        ready_after_a = graph.get_ready_steps({"a"})
        ready_ids = {n["id"] for n in ready_after_a}
        assert "b" in ready_ids
        assert "c" not in ready_ids

        ready = graph.get_ready_steps({"a", "b"})
        assert len(ready) == 1
        assert ready[0]["id"] == "c"

    def test_all_done_returns_empty(self):
        nodes = [_make_node("a"), _make_node("b")]
        edges = [_make_edge("a", "b")]
        graph = WorkflowGraph(nodes, edges)

        assert graph.get_ready_steps({"a", "b"}) == []


class TestBranchNodes:
    def test_branch_via_source_handle(self):
        nodes = [
            _make_node("cond", "condition"),
            _make_node("yes"),
            _make_node("no"),
        ]
        edges = [
            _make_edge("cond", "yes", sourceHandle="true"),
            _make_edge("cond", "no", sourceHandle="false"),
        ]
        graph = WorkflowGraph(nodes, edges)

        true_branch = graph.get_branch_nodes("cond", "true")
        assert "yes" in true_branch
        assert "no" not in true_branch

        false_branch = graph.get_branch_nodes("cond", "false")
        assert "no" in false_branch
        assert "yes" not in false_branch

    def test_branch_via_edge_data_condition(self):
        nodes = [
            _make_node("cond", "condition"),
            _make_node("yes"),
            _make_node("no"),
        ]
        edges = [
            _make_edge("cond", "yes", data={"condition": "true"}),
            _make_edge("cond", "no", data={"condition": "false"}),
        ]
        graph = WorkflowGraph(nodes, edges)

        true_branch = graph.get_branch_nodes("cond", "true")
        assert "yes" in true_branch

        false_branch = graph.get_branch_nodes("cond", "false")
        assert "no" in false_branch

    def test_branch_includes_descendants(self):
        nodes = [
            _make_node("cond", "condition"),
            _make_node("yes"),
            _make_node("yes_child"),
            _make_node("no"),
        ]
        edges = [
            _make_edge("cond", "yes", sourceHandle="true"),
            _make_edge("cond", "no", sourceHandle="false"),
            _make_edge("yes", "yes_child"),
        ]
        graph = WorkflowGraph(nodes, edges)

        true_branch = graph.get_branch_nodes("cond", "true")
        assert true_branch == {"yes", "yes_child"}


class TestUpstreamIds:
    def test_upstream_linear(self):
        nodes = [_make_node("a"), _make_node("b"), _make_node("c")]
        edges = [_make_edge("a", "b"), _make_edge("b", "c")]
        graph = WorkflowGraph(nodes, edges)

        assert graph.get_upstream_ids("c") == {"a", "b"}
        assert graph.get_upstream_ids("b") == {"a"}
        assert graph.get_upstream_ids("a") == set()

    def test_upstream_diamond(self):
        nodes = [_make_node("a"), _make_node("b"), _make_node("c"), _make_node("d")]
        edges = [
            _make_edge("a", "b"),
            _make_edge("a", "c"),
            _make_edge("b", "d"),
            _make_edge("c", "d"),
        ]
        graph = WorkflowGraph(nodes, edges)

        assert graph.get_upstream_ids("d") == {"a", "b", "c"}
