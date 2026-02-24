from __future__ import annotations

from app.engine.graph import WorkflowGraph
from app.engine.templates import extract_template_refs
from app.steps.registry import STEP_REGISTRY


def validate_workflow(definition: dict) -> list[str]:
    errors: list[str] = []
    nodes: list[dict] = definition.get("nodes", [])
    edges: list[dict] = definition.get("edges", [])

    if not nodes:
        errors.append("Workflow must have at least one node.")
        return errors

    node_ids = {n["id"] for n in nodes}
    node_map = {n["id"]: n for n in nodes}

    for edge in edges:
        if edge.get("source") not in node_ids:
            errors.append(f"Edge source {edge.get('source')!r} does not exist.")
        if edge.get("target") not in node_ids:
            errors.append(f"Edge target {edge.get('target')!r} does not exist.")

    if errors:
        return errors

    graph = WorkflowGraph(nodes, edges)
    if _has_cycle(graph, node_ids):
        errors.append("Workflow graph contains a cycle.")

    engine_handled_types = {"condition", "wait_for_approval"}
    for node in nodes:
        step_type = node.get("type", node.get("data", {}).get("type"))
        if step_type and step_type not in STEP_REGISTRY and step_type not in engine_handled_types:
            errors.append(f"Node {node['id']!r} has unregistered step type {step_type!r}.")

    for node in nodes:
        step_type = node.get("type", node.get("data", {}).get("type"))
        if step_type == "condition":
            outgoing = graph.get_outgoing_edges(node["id"])
            labels = set()
            for e in outgoing:
                label = e.get("data", {}).get("condition") or e.get("sourceHandle")
                if label:
                    labels.add(label)
            if "true" not in labels:
                errors.append(f"Condition node {node['id']!r} missing 'true' outgoing edge.")
            if "false" not in labels:
                errors.append(f"Condition node {node['id']!r} missing 'false' outgoing edge.")

    if len(nodes) > 1:
        connected = set()
        edge_set: set[str] = set()
        for edge in edges:
            edge_set.add(edge["source"])
            edge_set.add(edge["target"])
        for nid in node_ids:
            if nid in edge_set:
                connected.add(nid)
        orphans = node_ids - connected
        for orphan in orphans:
            errors.append(f"Node {orphan!r} is orphaned (not connected to any edge).")

    for node in nodes:
        config = node.get("data", {}).get("config", {})
        refs = extract_template_refs(config)
        upstream = graph.get_upstream_ids(node["id"])
        for ref in refs:
            root = ref.split(".")[0]
            if root != "input" and root not in upstream:
                errors.append(
                    f"Node {node['id']!r} references {root!r} which is not an upstream step."
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

    return any(dfs(n) for n in (node_ids - visited))
