import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router";
import { workflowsApi } from "../api/workflows";

export default function WorkflowList() {
  const { data: workflows, isLoading } = useQuery({
    queryKey: ["workflows"],
    queryFn: workflowsApi.list,
  });

  if (isLoading) {
    return <div className="p-8">Loading workflows...</div>;
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Workflows</h1>
        <Link
          to="/workflows/new/edit"
          className="px-4 py-2 bg-indigo-600 rounded-lg hover:bg-indigo-500 transition-colors"
        >
          New Workflow
        </Link>
      </div>
      <div className="grid gap-4">
        {workflows?.map((wf) => (
          <div
            key={wf.id}
            className="p-4 rounded-lg border border-slate-700 bg-slate-800 flex items-center justify-between"
          >
            <div>
              <h2 className="font-semibold">{wf.name}</h2>
              {wf.description && <p className="text-slate-400 text-sm">{wf.description}</p>}
            </div>
            <div className="flex gap-2">
              <Link
                to={`/workflows/${wf.id}/edit`}
                className="px-3 py-1 text-sm bg-slate-700 rounded hover:bg-slate-600"
              >
                Edit
              </Link>
              <Link
                to={`/workflows/${wf.id}/runs`}
                className="px-3 py-1 text-sm bg-slate-700 rounded hover:bg-slate-600"
              >
                Runs
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
