import { create } from "zustand";
import type { WorkflowNode, WorkflowEdge } from "@shared/types/workflow";

interface WorkflowState {
  workflowId: string | null;
  name: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  selectedNodeId: string | null;
  isDirty: boolean;

  setWorkflow: (id: string, name: string, nodes: WorkflowNode[], edges: WorkflowEdge[]) => void;
  setNodes: (nodes: WorkflowNode[]) => void;
  setEdges: (edges: WorkflowEdge[]) => void;
  setSelectedNode: (id: string | null) => void;
  markClean: () => void;
}

export const useWorkflowStore = create<WorkflowState>((set) => ({
  workflowId: null,
  name: "Untitled Workflow",
  nodes: [],
  edges: [],
  selectedNodeId: null,
  isDirty: false,

  setWorkflow: (id, name, nodes, edges) =>
    set({ workflowId: id, name, nodes, edges, isDirty: false }),
  setNodes: (nodes) => set({ nodes, isDirty: true }),
  setEdges: (edges) => set({ edges, isDirty: true }),
  setSelectedNode: (id) => set({ selectedNodeId: id }),
  markClean: () => set({ isDirty: false }),
}));
