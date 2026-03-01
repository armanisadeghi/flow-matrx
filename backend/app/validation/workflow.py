from __future__ import annotations

from app.engine.graph import WorkflowGraph
from app.engine.templates import extract_template_refs
from app.steps.registry import STEP_REGISTRY

# Step types the engine handles directly (not via STEP_REGISTRY lookup)
_ENGINE_HANDLED_TYPES = {"condition", "wait_for_approval", "wait_for_event", "for_each"}


def validate_workflow(definition: dict) -> list[str]:
    errors: list[str] = []
    nodes: list[dict] = definition.get("nodes", [])
    edges: list[dict] = definition.get("edges", [])

    if not nodes:
        errors.append("Workflow must have at least one node.")
        return errors

    # -- structural checks ------------------------------------------------

    node_ids = {n["id"] for n in nodes}

    for edge in edges:
        if edge.get("source") not in node_ids:
            errors.append(f"Edge source {edge.get('source')!r} does not exist.")
        if edge.get("target") not in node_ids:
            errors.append(f"Edge target {edge.get('target')!r} does not exist.")

    if errors:
        return errors

    graph = WorkflowGraph(nodes, edges)

    # -- cycle detection (uses graph.has_cycle now) -----------------------

    if graph.has_cycle():
        errors.append("Workflow graph contains a cycle.")

    # -- step type validation ---------------------------------------------

    for node in nodes:
        step_type = _node_type(node)
        if step_type and step_type not in STEP_REGISTRY and step_type not in _ENGINE_HANDLED_TYPES:
            errors.append(f"Node {node['id']!r} has unregistered step type {step_type!r}.")

    # -- condition branch validation --------------------------------------

    for node in nodes:
        step_type = _node_type(node)
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

    # -- orphan detection -------------------------------------------------

    if len(nodes) > 1:
        edge_set: set[str] = set()
        for edge in edges:
            edge_set.add(edge["source"])
            edge_set.add(edge["target"])
        orphans = node_ids - edge_set
        for orphan in orphans:
            errors.append(f"Node {orphan!r} is orphaned (not connected to any edge).")

    # -- template reference validation ------------------------------------

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

    # -- for_each validation ----------------------------------------------

    for node in nodes:
        step_type = _node_type(node)
        if step_type == "for_each":
            config = node.get("data", {}).get("config", {})
            if "items" not in config and not extract_template_refs(config):
                errors.append(
                    f"for_each node {node['id']!r} must have an 'items' config "
                    f"(static list or template reference)."
                )

    return errors


def _node_type(node: dict) -> str | None:
    return node.get("type", node.get("data", {}).get("type"))
