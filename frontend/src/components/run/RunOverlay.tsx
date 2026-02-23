import { useRunStore } from "../../stores/runStore";
import type { StepRunStatus } from "@shared/types/run";

const STATUS_COLORS: Record<StepRunStatus, string> = {
  pending: "bg-slate-500",
  running: "bg-blue-500 animate-pulse",
  completed: "bg-green-500",
  failed: "bg-red-500",
  skipped: "bg-slate-600",
  waiting_approval: "bg-yellow-500",
};

interface RunOverlayProps {
  nodeId: string;
}

export default function RunOverlay({ nodeId }: RunOverlayProps) {
  const stepRuns = useRunStore((s) => s.stepRunsById);
  const stepRun = Object.values(stepRuns).find((sr) => sr.stepId === nodeId);

  if (!stepRun) return null;

  return (
    <div
      className={`absolute inset-0 rounded-lg border-2 ${STATUS_COLORS[stepRun.status]} opacity-40 pointer-events-none`}
    />
  );
}
