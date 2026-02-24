import { useEffect } from "react";
import { useParams } from "react-router";
import { useQuery } from "@tanstack/react-query";
import { runsApi } from "../api/runs";
import { useRunStore } from "../stores/runStore";
import { useRunStream } from "../hooks/useRunStream";
import RunControls from "../components/run/RunControls";
import StepOutput from "../components/run/StepOutput";
import StatusBadge from "../components/shared/StatusBadge";
import ConnectionIndicator from "../components/run/ConnectionIndicator";

export default function RunDetail() {
  const { runId } = useParams<{ runId: string }>();

  // One-shot REST fetch to get the run metadata (id, workflowId, etc.)
  // staleTime: Infinity because live status comes from WebSocket, not polling.
  const { data: initialRun } = useQuery({
    queryKey: ["run", runId],
    queryFn: () => runsApi.get(runId!),
    enabled: !!runId,
    staleTime: Infinity,
  });

  // Connect to the WebSocket stream — writes all live state into runStore.
  useRunStream(runId ?? null);

  // Read live state from the store, not the Query cache.
  const runStatus = useRunStore((s) => s.runStatus);
  const stepsByStepId = useRunStore((s) => s.stepsByStepId);
  const connected = useRunStore((s) => s.connected);
  const activeRunId = useRunStore((s) => s.activeRunId);

  // Reset the store when we navigate away.
  const reset = useRunStore((s) => s.reset);
  useEffect(() => () => reset(), [reset]);

  if (!initialRun && !activeRunId) {
    return <div className="p-8 text-slate-400">Loading run...</div>;
  }

  const displayRunId = runId ?? activeRunId ?? "";
  // Use live status from store; fall back to initial REST response while connecting.
  const displayStatus = runStatus ?? initialRun?.status ?? "pending";
  const steps = Object.values(stepsByStepId);

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Run Detail</h1>
          <p className="font-mono text-sm text-slate-400">{displayRunId}</p>
        </div>
        <div className="flex items-center gap-4">
          <ConnectionIndicator connected={connected} />
          <StatusBadge status={displayStatus} />
          <RunControls runId={displayRunId} status={displayStatus} />
        </div>
      </div>

      {steps.length === 0 ? (
        <p className="text-slate-500 text-sm">Waiting for steps to begin...</p>
      ) : (
        <div className="grid gap-4">
          {steps.map((step) => (
            <StepOutput key={step.stepId} step={step} />
          ))}
        </div>
      )}
    </div>
  );
}
