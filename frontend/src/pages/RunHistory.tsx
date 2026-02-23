import { useParams, Link } from "react-router";
import { useQuery } from "@tanstack/react-query";
import { runsApi } from "../api/runs";
import StatusBadge from "../components/shared/StatusBadge";

export default function RunHistory() {
  const { workflowId } = useParams<{ workflowId: string }>();

  const { data: runs, isLoading } = useQuery({
    queryKey: ["runs", workflowId],
    queryFn: () => runsApi.listForWorkflow(workflowId!),
    enabled: !!workflowId,
  });

  if (isLoading) return <div className="p-8">Loading runs...</div>;

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">Run History</h1>
      <div className="grid gap-3">
        {runs?.map((run) => (
          <Link
            key={run.id}
            to={`/runs/${run.id}`}
            className="p-4 rounded-lg border border-slate-700 bg-slate-800 flex items-center justify-between hover:bg-slate-700"
          >
            <div>
              <p className="font-mono text-sm text-slate-400">{run.id}</p>
              <p className="text-sm mt-1">{run.startedAt}</p>
            </div>
            <StatusBadge status={run.status} />
          </Link>
        ))}
      </div>
    </div>
  );
}
