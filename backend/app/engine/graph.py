"""Graph helper: adjacency list, ready-step detection, branch resolution."""
from __future__ import annotations

from typing import Any


class WorkflowGraph:
    def __init__(self, nodes: list[dict], edges: list[dict]) -> None:
        self._nodes: dict[str, dict] = {n["id"]: n for n in nodes}
        self._edges = edges
        self._adjacency: dict[str, list[str]] = {n["id"]: [] for n in nodes}
        self._in_degree: dict[str, int] = {n["id"]: 0 for n in nodes}

        for edge in edges:
            self._adjacency[edge["source"]].append(edge["target"])
            self._in_degree[edge["target"]] += 1

    def get_node(self, node_id: str) -> dict[str, Any]:
        return self._nodes[node_id]

    def get_ready_steps(self, completed: set[str]) -> list[str]:
        """Return steps whose all predecessors have completed."""
        ready = []
        for node_id in self._nodes:
            if node_id in completed:
                continue
            predecessors = [
                e["source"] for e in self._edges if e["target"] == node_id
            ]
            if all(p in completed for p in predecessors):
                ready.append(node_id)
        return ready

    def get_downstream(self, node_id: str) -> list[str]:
        return self._adjacency.get(node_id, [])

    def get_outgoing_edges(self, node_id: str) -> list[dict]:
        return [e for e in self._edges if e["source"] == node_id]
