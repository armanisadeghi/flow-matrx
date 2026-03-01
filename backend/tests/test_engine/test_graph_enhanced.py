"""Tests for the enhanced WorkflowGraph features."""

from __future__ import annotations

import pytest

from app.engine.graph import WorkflowGraph


def _node(nid: str, ntype: str = "http_request") -> dict:
    return {"id": nid, "type": ntype, "data": {"label": nid, "config": {}}}


def _edge(src: str, tgt: str, **kw: object) -> dict:
    e = {"id": f"{src}-{tgt}", "source": src, "target": tgt}
    e.update(kw)
    return e


class TestTopologicalSort:
    def test_linear(self) -> None:
        graph = WorkflowGraph(
            [_node("a"), _node("b"), _node("c")],
            [_edge("a", "b"), _edge("b", "c")],
        )
        order = graph.topological_sort()
        assert order.index("a") < order.index("b") < order.index("c")

    def test_parallel(self) -> None:
        graph = WorkflowGraph(
            [_node("a"), _node("b"), _node("c")],
            [_edge("a", "c"), _edge("b", "c")],
        )
        order = graph.topological_sort()
        assert order.index("a") < order.index("c")
        assert order.index("b") < order.index("c")

    def test_cycle_raises(self) -> None:
        graph = WorkflowGraph(
            [_node("a"), _node("b")],
            [_edge("a", "b"), _edge("b", "a")],
        )
        with pytest.raises(ValueError, match="cycle"):
            graph.topological_sort()


class TestHasCycle:
    def test_no_cycle(self) -> None:
        graph = WorkflowGraph(
            [_node("a"), _node("b")],
            [_edge("a", "b")],
        )
        assert graph.has_cycle() is False

    def test_with_cycle(self) -> None:
        graph = WorkflowGraph(
            [_node("a"), _node("b"), _node("c")],
            [_edge("a", "b"), _edge("b", "c"), _edge("c", "a")],
        )
        assert graph.has_cycle() is True


class TestExecutionLevels:
    def test_linear_levels(self) -> None:
        graph = WorkflowGraph(
            [_node("a"), _node("b"), _node("c")],
            [_edge("a", "b"), _edge("b", "c")],
        )
        levels = graph.execution_levels()
        assert levels == [["a"], ["b"], ["c"]]

    def test_parallel_levels(self) -> None:
        graph = WorkflowGraph(
            [_node("a"), _node("b"), _node("c"), _node("d")],
            [_edge("a", "b"), _edge("a", "c"), _edge("b", "d"), _edge("c", "d")],
        )
        levels = graph.execution_levels()
        assert levels[0] == ["a"]
        assert set(levels[1]) == {"b", "c"}
        assert levels[2] == ["d"]


class TestExclusiveBranchNodes:
    def test_diamond_merge_not_skipped(self) -> None:
        """When branches merge at a common node, that node shouldn't be skipped."""
        nodes = [
            _node("cond", "condition"),
            _node("yes"),
            _node("no"),
            _node("merge"),
        ]
        edges = [
            _edge("cond", "yes", sourceHandle="true"),
            _edge("cond", "no", sourceHandle="false"),
            _edge("yes", "merge"),
            _edge("no", "merge"),
        ]
        graph = WorkflowGraph(nodes, edges)

        # Skipping the "false" branch should NOT include "merge"
        exclusive = graph.get_exclusive_branch_nodes("cond", "false")
        assert "no" in exclusive
        assert "merge" not in exclusive

    def test_exclusive_without_merge(self) -> None:
        """When branches don't merge, exclusive == full branch."""
        nodes = [
            _node("cond", "condition"),
            _node("yes"),
            _node("no"),
        ]
        edges = [
            _edge("cond", "yes", sourceHandle="true"),
            _edge("cond", "no", sourceHandle="false"),
        ]
        graph = WorkflowGraph(nodes, edges)

        exclusive = graph.get_exclusive_branch_nodes("cond", "false")
        assert exclusive == {"no"}


class TestSubgraph:
    def test_subgraph_extraction(self) -> None:
        graph = WorkflowGraph(
            [_node("a"), _node("b"), _node("c"), _node("d")],
            [_edge("a", "b"), _edge("b", "c"), _edge("c", "d")],
        )
        sub = graph.subgraph({"b", "c"})
        assert sub.node_ids == {"b", "c"}
        assert sub.edge_count == 1  # Only b→c


class TestNodeAccessors:
    def test_get_node_type(self) -> None:
        graph = WorkflowGraph([_node("a", "condition")], [])
        assert graph.get_node_type("a") == "condition"

    def test_get_node_label(self) -> None:
        graph = WorkflowGraph([_node("a")], [])
        assert graph.get_node_label("a") == "a"

    def test_leaf_ids(self) -> None:
        graph = WorkflowGraph(
            [_node("a"), _node("b"), _node("c")],
            [_edge("a", "b"), _edge("b", "c")],
        )
        assert graph.leaf_ids == ["c"]

    def test_node_count(self) -> None:
        graph = WorkflowGraph([_node("a"), _node("b")], [])
        assert graph.node_count == 2


class TestCriticalPath:
    def test_linear_critical_path(self) -> None:
        graph = WorkflowGraph(
            [_node("a"), _node("b"), _node("c")],
            [_edge("a", "b"), _edge("b", "c")],
        )
        assert graph.get_critical_path() == ["a", "b", "c"]

    def test_diamond_critical_path(self) -> None:
        graph = WorkflowGraph(
            [_node("a"), _node("b"), _node("c"), _node("d"), _node("e")],
            [
                _edge("a", "b"),
                _edge("a", "c"),
                _edge("b", "d"),
                _edge("c", "d"),
                _edge("d", "e"),
            ],
        )
        path = graph.get_critical_path()
        # Longest path is a→b→d→e or a→c→d→e (both length 4)
        assert len(path) == 4
        assert path[0] == "a"
        assert path[-1] == "e"


class TestGetNodesByType:
    def test_finds_matching(self) -> None:
        graph = WorkflowGraph(
            [_node("a", "http_request"), _node("b", "condition"), _node("c", "http_request")],
            [],
        )
        http_nodes = graph.get_nodes_by_type("http_request")
        ids = {n["id"] for n in http_nodes}
        assert ids == {"a", "c"}
