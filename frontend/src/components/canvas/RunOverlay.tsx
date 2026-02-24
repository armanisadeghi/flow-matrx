import { useRunStore } from "../../stores/runStore";
import type { StepRunStatus } from "@shared/types/run";

const STATUS_RING: Record<StepRunStatus, string> = {
  pending: "border-slate-600 opacity-0",
  running: "border-blue-400 opacity-60 animate-pulse shadow-[0_0_12px_2px_rgba(96,165,250,0.4)]",
  completed: "border-green-400 opacity-50",
  failed: "border-red-500 opacity-60",
  skipped: "border-slate-600 opacity-30",
  waiting_approval: "border-yellow-400 opacity-60",
};

interface RunOverlayProps {
  nodeId: string;
}

export default function RunOverlay({ nodeId }: RunOverlayProps) {
  const step = useRunStore((s) => s.stepsByStepId[nodeId]);

  if (!step || step.status === "pending") return null;

  return (
    <div
      className={`absolute inset-0 rounded-lg border-2 pointer-events-none transition-all duration-300 ${STATUS_RING[step.status]}`}
    />
  );
}
