from __future__ import annotations

from collections import deque
from typing import Any


class WorkflowGraph:
    def __init__(self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> None:
        self._nodes: dict[str, dict[str, Any]] = {n["id"]: n for n in nodes}
        self._edges = edges

        self._children: dict[str, list[str]] = {n["id"]: [] for n in nodes}
        self._parents: dict[str, list[str]] = {n["id"]: [] for n in nodes}
        self._edge_index: dict[str, list[dict[str, Any]]] = {n["id"]: [] for n in nodes}

        for edge in edges:
            src, tgt = edge["source"], edge["target"]
            if src in self._children and tgt in self._parents:
                self._children[src].append(tgt)
                self._parents[tgt].append(src)
                self._edge_index[src].append(edge)

        self.root_ids: list[str] = [
            nid for nid, parents in self._parents.items() if not parents
        ]
        self.leaf_ids: list[str] = [
            nid for nid, children in self._children.items() if not children
        ]

    # -- node access -----------------------------------------------------------

    def get_node(self, node_id: str) -> dict[str, Any]:
        return self._nodes[node_id]

    def get_node_type(self, node_id: str) -> str:
        node = self._nodes[node_id]
        return node.get("type", node.get("data", {}).get("type", "unknown"))

    def get_node_data(self, node_id: str) -> dict[str, Any]:
        return self._nodes[node_id].get("data", {})

    def get_node_config(self, node_id: str) -> dict[str, Any]:
        return self.get_node_data(node_id).get("config", {})

    def get_node_label(self, node_id: str) -> str:
        return self.get_node_data(node_id).get("label", node_id)

    @property
    def node_ids(self) -> set[str]:
        return set(self._nodes.keys())

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        return len(self._edges)

    # -- traversal -------------------------------------------------------------

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

    def get_upstream(self, node_id: str) -> list[str]:
        return self._parents.get(node_id, [])

    def get_outgoing_edges(self, node_id: str) -> list[dict[str, Any]]:
        return self._edge_index.get(node_id, [])

    def get_incoming_edges(self, node_id: str) -> list[dict[str, Any]]:
        return [e for e in self._edges if e["target"] == node_id]

    # -- topological sort (Kahn's algorithm) -----------------------------------

    def topological_sort(self) -> list[str]:
        """Return nodes in topological order.  Raises ValueError if graph has a cycle."""
        in_degree: dict[str, int] = {nid: len(p) for nid, p in self._parents.items()}
        queue: deque[str] = deque(nid for nid, d in in_degree.items() if d == 0)
        order: list[str] = []

        while queue:
            nid = queue.popleft()
            order.append(nid)
            for child in self._children.get(nid, []):
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        if len(order) != len(self._nodes):
            raise ValueError("Workflow graph contains a cycle")
        return order

    def has_cycle(self) -> bool:
        try:
            self.topological_sort()
            return False
        except ValueError:
            return True

    # -- execution levels (parallelism tiers) ----------------------------------

    def execution_levels(self) -> list[list[str]]:
        """Group nodes into levels where all nodes in a level can run in parallel.

        Level 0 = root nodes, level N = nodes whose parents are all in levels < N.
        """
        in_degree: dict[str, int] = {nid: len(p) for nid, p in self._parents.items()}
        current: list[str] = [nid for nid, d in in_degree.items() if d == 0]
        levels: list[list[str]] = []

        while current:
            levels.append(current)
            next_level: list[str] = []
            for nid in current:
                for child in self._children.get(nid, []):
                    in_degree[child] -= 1
                    if in_degree[child] == 0:
                        next_level.append(child)
            current = next_level

        return levels

    # -- branch analysis -------------------------------------------------------

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

    def get_exclusive_branch_nodes(
        self, condition_id: str, branch_label: str
    ) -> set[str]:
        """Like get_branch_nodes but excludes nodes reachable from other branches.

        This handles diamond-shaped merges after a condition — the merge node
        should NOT be skipped just because one branch was skipped.
        """
        target_branch = self.get_branch_nodes(condition_id, branch_label)
        other_edges = [
            e for e in self._edges
            if e["source"] == condition_id
            and e.get("data", {}).get("condition") != branch_label
            and e.get("sourceHandle") != branch_label
        ]
        reachable_from_other: set[str] = set()
        for edge in other_edges:
            reachable_from_other.add(edge["target"])
            reachable_from_other |= self._all_descendants(edge["target"])

        return target_branch - reachable_from_other

    def _all_descendants(self, node_id: str) -> set[str]:
        descendants: set[str] = set()
        stack = list(self._children.get(node_id, []))
        while stack:
            current = stack.pop()
            if current not in descendants:
                descendants.add(current)
                stack.extend(self._children.get(current, []))
        return descendants

    # -- ancestor analysis -----------------------------------------------------

    def get_upstream_ids(self, node_id: str) -> set[str]:
        ancestors: set[str] = set()
        stack = list(self._parents.get(node_id, []))
        while stack:
            current = stack.pop()
            if current not in ancestors:
                ancestors.add(current)
                stack.extend(self._parents.get(current, []))
        return ancestors

    # -- subgraph extraction ---------------------------------------------------

    def subgraph(self, node_ids: set[str]) -> WorkflowGraph:
        """Create a new graph containing only the specified nodes and their edges."""
        nodes = [self._nodes[nid] for nid in node_ids if nid in self._nodes]
        edges = [
            e for e in self._edges
            if e["source"] in node_ids and e["target"] in node_ids
        ]
        return WorkflowGraph(nodes, edges)

    # -- introspection ---------------------------------------------------------

    def get_nodes_by_type(self, step_type: str) -> list[dict[str, Any]]:
        return [
            node for node in self._nodes.values()
            if self.get_node_type(node["id"]) == step_type
        ]

    def get_critical_path(self) -> list[str]:
        """Return the longest path through the graph (by node count)."""
        topo = self.topological_sort()
        dist: dict[str, int] = {nid: 0 for nid in topo}
        prev: dict[str, str | None] = {nid: None for nid in topo}

        for nid in topo:
            for child in self._children.get(nid, []):
                if dist[nid] + 1 > dist[child]:
                    dist[child] = dist[nid] + 1
                    prev[child] = nid

        end = max(dist, key=lambda n: dist[n])
        path: list[str] = []
        current: str | None = end
        while current is not None:
            path.append(current)
            current = prev[current]
        path.reverse()
        return path
