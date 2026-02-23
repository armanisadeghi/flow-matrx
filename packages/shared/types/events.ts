import type { RunStatus, StepRunStatus } from "./run.js";

export type WebSocketEventType =
  | "run.started"
  | "run.completed"
  | "run.failed"
  | "run.paused"
  | "run.cancelled"
  | "step.started"
  | "step.completed"
  | "step.failed"
  | "step.waiting_approval"
  | "approval.required";

export interface BaseEvent {
  type: WebSocketEventType;
  runId: string;
  timestamp: string;
}

export interface RunStatusEvent extends BaseEvent {
  type: "run.started" | "run.completed" | "run.failed" | "run.paused" | "run.cancelled";
  status: RunStatus;
  errorMessage?: string;
}

export interface StepStatusEvent extends BaseEvent {
  type: "step.started" | "step.completed" | "step.failed" | "step.waiting_approval";
  stepRunId: string;
  stepId: string;
  status: StepRunStatus;
  output?: Record<string, unknown>;
  error?: string;
}

export interface ApprovalRequiredEvent extends BaseEvent {
  type: "approval.required";
  stepRunId: string;
  stepId: string;
  approvalPrompt?: string;
}

export type WorkflowEvent = RunStatusEvent | StepStatusEvent | ApprovalRequiredEvent;
