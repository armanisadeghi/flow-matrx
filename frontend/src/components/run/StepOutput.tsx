import type { StepRun } from "@shared/types/run";
import StatusBadge from "../shared/StatusBadge";

interface StepOutputProps {
  stepRun: StepRun;
}

export default function StepOutput({ stepRun }: StepOutputProps) {
  return (
    <div className="rounded-lg border border-slate-700 bg-slate-800 p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="font-mono text-sm">{stepRun.stepId}</span>
        <StatusBadge status={stepRun.status} />
      </div>
      {stepRun.output && (
        <pre className="text-xs bg-slate-900 rounded p-3 overflow-x-auto text-slate-300">
          {JSON.stringify(stepRun.output, null, 2)}
        </pre>
      )}
      {stepRun.error && (
        <p className="text-red-400 text-sm mt-2">{stepRun.error}</p>
      )}
    </div>
  );
}
