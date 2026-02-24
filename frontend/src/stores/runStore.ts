import { create } from "zustand";
import type { RunStatus, StepRunStatus } from "@shared/types/run";
import type { SnapshotEvent } from "@shared/types/events";

export interface StepState {
  stepId: string;
  stepType: string;
  status: StepRunStatus;
  attempt: number;
  output?: Record<string, unknown>;
  error: string | null;
}

interface RunStore {
  // Connection
  connected: boolean;
  reconnectAttempt: number;

  // Run-level state
  activeRunId: string | null;
  runStatus: RunStatus | null;
  context: Record<string, unknown>;

  // Step-level state keyed by step_id (node id from React Flow)
  stepsByStepId: Record<string, StepState>;

  // Actions
  setConnected: (connected: boolean) => void;
  setReconnectAttempt: (n: number) => void;
  loadSnapshot: (snapshot: SnapshotEvent) => void;
  setRunStatus: (status: RunStatus) => void;
  setStepStatus: (
    stepId: string,
    status: StepRunStatus,
    extras?: { attempt?: number; output?: Record<string, unknown>; error?: string | null },
  ) => void;
  setContext: (context: Record<string, unknown>) => void;
  reset: () => void;
}

const INITIAL_STATE = {
  connected: false,
  reconnectAttempt: 0,
  activeRunId: null,
  runStatus: null,
  context: {},
  stepsByStepId: {},
};

export const useRunStore = create<RunStore>((set) => ({
  ...INITIAL_STATE,

  setConnected: (connected) => set({ connected }),

  setReconnectAttempt: (reconnectAttempt) => set({ reconnectAttempt }),

  loadSnapshot: (snapshot) =>
    set({
      activeRunId: snapshot.run_id,
      runStatus: snapshot.run_status,
      context: snapshot.context,
      stepsByStepId: Object.fromEntries(
        snapshot.steps.map((s) => [
          s.step_id,
          {
            stepId: s.step_id,
            stepType: s.step_type,
            status: s.status,
            attempt: s.attempt,
            error: s.error,
          },
        ]),
      ),
    }),

  setRunStatus: (runStatus) => set({ runStatus }),

  setStepStatus: (stepId, status, extras = {}) =>
    set((state) => ({
      stepsByStepId: {
        ...state.stepsByStepId,
        [stepId]: {
          ...(state.stepsByStepId[stepId] ?? {
            stepId,
            stepType: "unknown",
            attempt: 1,
            error: null,
          }),
          status,
          ...(extras.attempt !== undefined ? { attempt: extras.attempt } : {}),
          ...(extras.output !== undefined ? { output: extras.output } : {}),
          ...(extras.error !== undefined ? { error: extras.error ?? null } : {}),
        },
      },
    })),

  setContext: (context) => set({ context }),

  reset: () => set(INITIAL_STATE),
}));
