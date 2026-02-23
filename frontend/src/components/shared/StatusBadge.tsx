import type { RunStatus, StepRunStatus } from "@shared/types/run";

type Status = RunStatus | StepRunStatus;

const STATUS_STYLES: Record<Status, string> = {
  pending: "bg-slate-700 text-slate-300",
  running: "bg-blue-900 text-blue-300",
  paused: "bg-yellow-900 text-yellow-300",
  completed: "bg-green-900 text-green-300",
  failed: "bg-red-900 text-red-300",
  cancelled: "bg-slate-700 text-slate-400",
  skipped: "bg-slate-800 text-slate-500",
  waiting_approval: "bg-amber-900 text-amber-300",
};

interface StatusBadgeProps {
  status: Status;
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${STATUS_STYLES[status]}`}>
      {status.replace(/_/g, " ")}
    </span>
  );
}
