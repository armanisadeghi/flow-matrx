import { useEffect } from "react";
import { createRunWebSocket } from "../api/ws";
import { useRunStore } from "../stores/runStore";
import type {
  WorkflowEvent,
  SnapshotEvent,
  RunStatusEvent,
  StepStatusEvent,
  ContextUpdatedEvent,
} from "@shared/types/events";
import type { StepRunStatus } from "@shared/types/run";

function handleSnapshot(event: SnapshotEvent): void {
  useRunStore.getState().loadSnapshot(event);
}

function handleRunStatus(event: RunStatusEvent): void {
  useRunStore.getState().setRunStatus(event.payload.status);
}

// Map event type to canonical StepRunStatus for events that don't carry status in payload.
const EVENT_TYPE_TO_STATUS: Partial<Record<string, StepRunStatus>> = {
  "step.started": "running",
  "step.completed": "completed",
  "step.failed": "failed",
  "step.skipped": "skipped",
  "step.waiting": "waiting_approval",
  "step.retrying": "running",
} as const;

function handleStepStatus(event: StepStatusEvent): void {
  const { setStepStatus } = useRunStore.getState();
  const status =
    (event.payload as { status?: StepRunStatus }).status ??
    EVENT_TYPE_TO_STATUS[event.type] ??
    "pending";
  setStepStatus(event.step_id, status, {
    attempt: event.payload.attempt,
    output: event.payload.output,
    error: event.payload.error,
  });
}

function handleContextUpdated(event: ContextUpdatedEvent): void {
  useRunStore.getState().setContext(event.payload.context);
}

function dispatch(event: WorkflowEvent): void {
  switch (event.type) {
    case "snapshot":
      handleSnapshot(event);
      break;

    case "run.started":
    case "run.completed":
    case "run.failed":
    case "run.paused":
    case "run.resumed":
    case "run.cancelled":
      handleRunStatus(event as RunStatusEvent);
      break;

    case "step.started":
    case "step.completed":
    case "step.failed":
    case "step.skipped":
    case "step.waiting":
    case "step.retrying":
      handleStepStatus(event as StepStatusEvent);
      break;

    case "context.updated":
      handleContextUpdated(event as ContextUpdatedEvent);
      break;

    default:
      console.warn("[useRunStream] Unrecognised event type", (event as WorkflowEvent).type);
  }
}

/**
 * Connects to the WebSocket event stream for the given run.
 * Writes all state into the Zustand runStore.
 * Components should read from the store, NOT from this hook's return value.
 *
 * Dedup guarantee: snapshot events from the server are always the authoritative
 * source of truth. If a live event arrives whose step_id already appears in the
 * snapshot with the same status (e.g. an event buffered during connect races with
 * the snapshot), setStepStatus is still called — it's an idempotent write and
 * Zustand's shallow equality prevents re-renders for unchanged values.
 */
export function useRunStream(runId: string | null): void {
  const setConnected = useRunStore((s) => s.setConnected);
  const setReconnectAttempt = useRunStore((s) => s.setReconnectAttempt);

  useEffect(() => {
    if (!runId) return;

    const handle = createRunWebSocket(
      runId,
      dispatch,
      (connected, attempt) => {
        setConnected(connected);
        setReconnectAttempt(attempt);
      },
    );

    return () => {
      handle.close();
      setConnected(false);
    };
  }, [runId, setConnected, setReconnectAttempt]);
}
