import type { RunStatus, StepRunStatus } from "./run.js";

export type WebSocketEventType =
  | "snapshot"
  | "run.started"
  | "run.completed"
  | "run.failed"
  | "run.paused"
  | "run.resumed"
  | "run.cancelled"
  | "step.started"
  | "step.completed"
  | "step.failed"
  | "step.skipped"
  | "step.waiting"
  | "step.retrying"
  | "context.updated";

// ──────────────────────────────────────────────
// Snapshot (sent once on connect / reconnect)
// ──────────────────────────────────────────────

export interface SnapshotStep {
  step_id: string;
  step_type: string;
  status: StepRunStatus;
  attempt: number;
  error: string | null;
}

export interface SnapshotEvent {
  type: "snapshot";
  run_id: string;
  run_status: RunStatus;
  context: Record<string, unknown>;
  steps: SnapshotStep[];
}

// ──────────────────────────────────────────────
// Live events (streamed after snapshot)
// ──────────────────────────────────────────────

export interface BaseEvent {
  type: WebSocketEventType;
  run_id: string;
  timestamp: string;
}

export interface RunStatusEvent extends BaseEvent {
  type:
    | "run.started"
    | "run.completed"
    | "run.failed"
    | "run.paused"
    | "run.resumed"
    | "run.cancelled";
  payload: {
    status: RunStatus;
    error?: string;
  };
}

export interface StepStatusEvent extends BaseEvent {
  type:
    | "step.started"
    | "step.completed"
    | "step.failed"
    | "step.skipped"
    | "step.waiting"
    | "step.retrying";
  step_id: string;
  payload: {
    status: StepRunStatus;
    attempt?: number;
    output?: Record<string, unknown>;
    error?: string;
  };
}

export interface ContextUpdatedEvent extends BaseEvent {
  type: "context.updated";
  step_id: string;
  payload: {
    context: Record<string, unknown>;
  };
}

export type LiveEvent = RunStatusEvent | StepStatusEvent | ContextUpdatedEvent;

export type WorkflowEvent = SnapshotEvent | LiveEvent;
