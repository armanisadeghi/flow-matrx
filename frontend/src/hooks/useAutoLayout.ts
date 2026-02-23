import { useCallback } from "react";
import dagre from "dagre";
import { useWorkflowStore } from "../stores/workflowStore";
import type { WorkflowNode, WorkflowEdge } from "@shared/types/workflow";

const NODE_WIDTH = 180;
const NODE_HEIGHT = 60;

export function useAutoLayout() {
  const { nodes, edges, setNodes } = useWorkflowStore();

  return useCallback(() => {
    const g = new dagre.graphlib.Graph();
    g.setDefaultEdgeLabel(() => ({}));
    g.setGraph({ rankdir: "TB", nodesep: 40, ranksep: 60 });

    nodes.forEach((node) => {
      g.setNode(node.id, { width: NODE_WIDTH, height: NODE_HEIGHT });
    });

    edges.forEach((edge) => {
      g.setEdge(edge.source, edge.target);
    });

    dagre.layout(g);

    const layouted: WorkflowNode[] = nodes.map((node) => {
      const { x, y } = g.node(node.id);
      return { ...node, position: { x: x - NODE_WIDTH / 2, y: y - NODE_HEIGHT / 2 } };
    });

    setNodes(layouted);
  }, [nodes, edges, setNodes]);
}
