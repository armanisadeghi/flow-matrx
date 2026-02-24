from __future__ import annotations

from typing import Any


class WorkflowGraph:
    def __init__(self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> None:
        self._nodes: dict[str, dict[str, Any]] = {n["id"]: n for n in nodes}
        self._edges = edges

        self._children: dict[str, list[str]] = {n["id"]: [] for n in nodes}
        self._parents: dict[str, list[str]] = {n["id"]: [] for n in nodes}

        for edge in edges:
            src, tgt = edge["source"], edge["target"]
            if src in self._children and tgt in self._parents:
                self._children[src].append(tgt)
                self._parents[tgt].append(src)

        self.root_ids: list[str] = [
            nid for nid, parents in self._parents.items() if not parents
        ]

    def get_node(self, node_id: str) -> dict[str, Any]:
        return self._nodes[node_id]

    @property
    def node_ids(self) -> set[str]:
        return set(self._nodes.keys())

    def get_ready_steps(self, done_ids: set[str]) -> list[dict[str, Any]]:
        ready: list[dict[str, Any]] = []
        for nid, node in self._nodes.items():
            if nid in done_ids:
                continue
            if all(p in done_ids for p in self._parents[nid]):
                ready.append(node)
        return ready

    def get_downstream(self, node_id: str) -> list[str]:
        return self._children.get(node_id, [])

    def get_outgoing_edges(self, node_id: str) -> list[dict[str, Any]]:
        return [e for e in self._edges if e["source"] == node_id]

    def get_branch_nodes(self, condition_id: str, branch_label: str) -> set[str]:
        branch_edges = [
            e for e in self._edges
            if e["source"] == condition_id
            and (
                e.get("data", {}).get("condition") == branch_label
                or e.get("sourceHandle") == branch_label
            )
        ]
        result: set[str] = set()
        for edge in branch_edges:
            result.add(edge["target"])
            result |= self._all_descendants(edge["target"])
        return result

    def _all_descendants(self, node_id: str) -> set[str]:
        descendants: set[str] = set()
        stack = list(self._children.get(node_id, []))
        while stack:
            current = stack.pop()
            if current not in descendants:
                descendants.add(current)
                stack.extend(self._children.get(current, []))
        return descendants

    def get_upstream_ids(self, node_id: str) -> set[str]:
        ancestors: set[str] = set()
        stack = list(self._parents.get(node_id, []))
        while stack:
            current = stack.pop()
            if current not in ancestors:
                ancestors.add(current)
                stack.extend(self._parents.get(current, []))
        return ancestors
