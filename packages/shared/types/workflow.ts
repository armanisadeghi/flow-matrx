export type StepType =
  | "http_request"
  | "llm_call"
  | "inline_code"
  | "condition"
  | "database_query"
  | "transform"
  | "wait_for_approval"
  | "wait_for_event"
  | "send_email"
  | "webhook"
  | "delay"
  | "for_each";

export interface WorkflowNode {
  id: string;
  type: StepType;
  label: string;
  config: Record<string, unknown>;
  position: { x: number; y: number };
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  condition?: string;
  label?: string;
}

export interface WorkflowDefinition {
  id: string;
  name: string;
  description?: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  createdAt: string;
  updatedAt: string;
}
