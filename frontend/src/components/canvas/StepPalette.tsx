import type { StepType } from "@shared/types/workflow";

const STEP_TYPES: { type: StepType; label: string; color: string }[] = [
  { type: "http_request", label: "HTTP Request", color: "bg-blue-600" },
  { type: "llm_call", label: "LLM Call", color: "bg-purple-600" },
  { type: "inline_code", label: "Code", color: "bg-yellow-600" },
  { type: "condition", label: "Condition", color: "bg-orange-600" },
  { type: "database_query", label: "Database Query", color: "bg-green-600" },
  { type: "transform", label: "Transform", color: "bg-cyan-600" },
  { type: "wait_for_approval", label: "Approval", color: "bg-red-600" },
  { type: "wait_for_event", label: "Wait for Event", color: "bg-pink-600" },
  { type: "send_email", label: "Send Email", color: "bg-teal-600" },
  { type: "webhook", label: "Webhook", color: "bg-indigo-600" },
  { type: "delay", label: "Delay", color: "bg-slate-600" },
  { type: "for_each", label: "For Each", color: "bg-emerald-600" },
];

export default function StepPalette() {
  const onDragStart = (event: React.DragEvent, stepType: StepType) => {
    event.dataTransfer.setData("application/reactflow", stepType);
    event.dataTransfer.effectAllowed = "move";
  };

  return (
    <div className="w-56 border-r border-slate-700 bg-slate-800 p-3 overflow-y-auto">
      <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
        Steps
      </h2>
      <div className="grid gap-1.5">
        {STEP_TYPES.map(({ type, label, color }) => (
          <div
            key={type}
            className={`${color} text-white text-sm px-3 py-2 rounded cursor-grab active:cursor-grabbing select-none`}
            draggable
            onDragStart={(e) => onDragStart(e, type)}
          >
            {label}
          </div>
        ))}
      </div>
    </div>
  );
}
