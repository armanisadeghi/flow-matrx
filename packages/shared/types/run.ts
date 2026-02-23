export type RunStatus =
  | "pending"
  | "running"
  | "paused"
  | "completed"
  | "failed"
  | "cancelled";

export type StepRunStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed"
  | "skipped"
  | "waiting_approval";

export interface StepRun {
  id: string;
  runId: string;
  stepId: string;
  status: StepRunStatus;
  input: Record<string, unknown>;
  output?: Record<string, unknown>;
  error?: string;
  startedAt?: string;
  completedAt?: string;
}

export interface Run {
  id: string;
  workflowId: string;
  status: RunStatus;
  triggerPayload?: Record<string, unknown>;
  stepRuns: StepRun[];
  startedAt: string;
  completedAt?: string;
  errorMessage?: string;
}
