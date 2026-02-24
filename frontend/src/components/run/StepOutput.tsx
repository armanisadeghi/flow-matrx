import type { StepState } from "../../stores/runStore";
import StatusBadge from "../shared/StatusBadge";

interface StepOutputProps {
  step: StepState;
}

export default function StepOutput({ step }: StepOutputProps) {
  return (
    <div className="rounded-lg border border-slate-700 bg-slate-800 p-4">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="font-mono text-sm text-slate-300">{step.stepId}</span>
          <span className="text-xs text-slate-500 bg-slate-700 px-1.5 py-0.5 rounded">
            {step.stepType}
          </span>
          {step.attempt > 1 && (
            <span className="text-xs text-amber-400">attempt {step.attempt}</span>
          )}
        </div>
        <StatusBadge status={step.status} />
      </div>
      {step.output && (
        <pre className="text-xs bg-slate-900 rounded p-3 overflow-x-auto text-slate-300 mt-2">
          {JSON.stringify(step.output, null, 2)}
        </pre>
      )}
      {step.error && (
        <p className="text-red-400 text-sm mt-2">{step.error}</p>
      )}
    </div>
  );
}
