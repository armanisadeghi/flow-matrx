"""DAG validation and template reference checking."""
from __future__ import annotations

from app.engine.exceptions import WorkflowValidationError
from app.engine.graph import WorkflowGraph
from app.engine.templates import extract_template_refs


def validate_workflow(definition: dict) -> list[str]:
    """Validate a workflow definition and return a list of error messages."""
    errors: list[str] = []
    nodes: list[dict] = definition.get("nodes", [])
    edges: list[dict] = definition.get("edges", [])

    if not nodes:
        errors.append("Workflow must have at least one node.")

    node_ids = {n["id"] for n in nodes}

    for edge in edges:
        if edge.get("source") not in node_ids:
            errors.append(f"Edge source {edge.get('source')!r} does not exist.")
        if edge.get("target") not in node_ids:
            errors.append(f"Edge target {edge.get('target')!r} does not exist.")

    # Cycle detection via DFS
    graph = WorkflowGraph(nodes, edges)
    if _has_cycle(graph, node_ids):
        errors.append("Workflow graph contains a cycle.")

    # Template reference validation
    for node in nodes:
        refs = extract_template_refs(node.get("config", {}))
        for ref in refs:
            root = ref.split(".")[0]
            if root != "trigger" and root not in node_ids:
                errors.append(
                    f"Node {node['id']!r} references unknown step {root!r} in template."
                )

    return errors


def _has_cycle(graph: WorkflowGraph, node_ids: set[str]) -> bool:
    visited: set[str] = set()
    rec_stack: set[str] = set()

    def dfs(node_id: str) -> bool:
        visited.add(node_id)
        rec_stack.add(node_id)
        for neighbor in graph.get_downstream(node_id):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True
        rec_stack.discard(node_id)
        return False

    return any(dfs(n) for n in node_ids if n not in visited)
