import { useParams } from "react-router";
import { useQuery } from "@tanstack/react-query";
import { runsApi } from "../api/runs";
import { useRunStream } from "../hooks/useRunStream";
import RunControls from "../components/run/RunControls";
import StepOutput from "../components/run/StepOutput";
import StatusBadge from "../components/shared/StatusBadge";

export default function RunDetail() {
  const { runId } = useParams<{ runId: string }>();
  const { data: run } = useQuery({
    queryKey: ["run", runId],
    queryFn: () => runsApi.get(runId!),
    enabled: !!runId,
  });

  useRunStream(runId ?? null);

  if (!run) return <div className="p-8">Loading run...</div>;

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Run Detail</h1>
          <p className="font-mono text-sm text-slate-400">{run.id}</p>
        </div>
        <div className="flex items-center gap-4">
          <StatusBadge status={run.status} />
          <RunControls run={run} />
        </div>
      </div>
      <div className="grid gap-4">
        {run.stepRuns.map((sr) => (
          <StepOutput key={sr.id} stepRun={sr} />
        ))}
      </div>
    </div>
  );
}
