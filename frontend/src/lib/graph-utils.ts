import type { WorkflowNode, WorkflowEdge } from "@shared/types/workflow";

export function getUpstream(nodeId: string, edges: WorkflowEdge[]): string[] {
  return edges.filter((e) => e.target === nodeId).map((e) => e.source);
}

export function getDownstream(nodeId: string, edges: WorkflowEdge[]): string[] {
  return edges.filter((e) => e.source === nodeId).map((e) => e.target);
}

export function getRootNodes(nodes: WorkflowNode[], edges: WorkflowEdge[]): WorkflowNode[] {
  const targets = new Set(edges.map((e) => e.target));
  return nodes.filter((n) => !targets.has(n.id));
}
