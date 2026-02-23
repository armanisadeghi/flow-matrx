import { useEffect } from "react";
import { createRunWebSocket } from "../api/ws";
import { useRunStore } from "../stores/runStore";
import type { WorkflowEvent } from "@shared/types/events";

export function useRunStream(runId: string | null): void {
  const { updateStepRun } = useRunStore();

  useEffect(() => {
    if (!runId) return;

    const ws = createRunWebSocket(runId, (event: WorkflowEvent) => {
      if (event.type === "step.completed" || event.type === "step.failed") {
        updateStepRun({
          id: event.stepRunId,
          runId: event.runId,
          stepId: event.stepId,
          status: event.status,
          input: {},
          output: event.output,
          error: event.error,
        });
      }
    });

    return () => ws.close();
  }, [runId, updateStepRun]);
}
