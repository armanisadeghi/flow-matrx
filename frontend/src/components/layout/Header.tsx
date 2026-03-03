import { Link, useLocation, useParams } from "react-router";
import { Menu, Play } from "lucide-react";
import { useLayoutStore } from "../../stores/layoutStore";
import { useWorkflowStore } from "../../stores/workflowStore";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { runsApi } from "../../api/runs";

function Breadcrumbs() {
  const location = useLocation();
  const { workflowId, runId } = useParams();
  const workflowName = useWorkflowStore((s) => s.name);

  const segments: { label: string; to?: string }[] = [{ label: "Workflows", to: "/" }];

  if (location.pathname.includes("/edit") && workflowId) {
    segments.push({ label: workflowId === "new" ? "New Workflow" : workflowName });
  } else if (location.pathname.includes("/runs") && workflowId) {
    segments.push({ label: "Runs" });
  } else if (runId) {
    segments.push({ label: `Run ${runId.slice(0, 8)}` });
  }

  return (
    <nav className="flex items-center gap-1.5 text-sm">
      {segments.map((seg, i) => (
        <span key={seg.label} className="flex items-center gap-1.5">
          {i > 0 && <span className="text-slate-600">/</span>}
          {seg.to ? (
            <Link to={seg.to} className="text-slate-400 hover:text-slate-200 transition-colors">
              {seg.label}
            </Link>
          ) : (
            <span className="text-slate-200">{seg.label}</span>
          )}
        </span>
      ))}
    </nav>
  );
}

export default function Header() {
  const toggleSidebar = useLayoutStore((s) => s.toggleSidebar);
  const { workflowId } = useParams();
  const queryClient = useQueryClient();
  const isBuilder = workflowId && workflowId !== "new";

  const triggerRun = useMutation({
    mutationFn: () => runsApi.trigger(workflowId!, {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["runs"] }),
  });

  return (
    <header className="h-11 flex items-center justify-between px-3 border-b border-slate-700 bg-slate-900 shrink-0">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={toggleSidebar}
          className="p-1.5 rounded hover:bg-slate-700 transition-colors text-slate-400 hover:text-slate-200"
        >
          <Menu size={16} />
        </button>
        <Link to="/" className="text-sm font-bold tracking-tight text-indigo-400">
          Flow Matrx
        </Link>
        <Breadcrumbs />
      </div>
      <div className="flex items-center gap-2">
        {isBuilder && (
          <button
            type="button"
            onClick={() => triggerRun.mutate()}
            disabled={triggerRun.isPending}
            className="flex items-center gap-1.5 px-3 py-1 text-xs bg-emerald-600 hover:bg-emerald-500 rounded transition-colors disabled:opacity-50"
          >
            <Play size={12} />
            Run
          </button>
        )}
      </div>
    </header>
  );
}
