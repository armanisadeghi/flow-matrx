import { Handle, Position } from "@xyflow/react";
import RunOverlay from "../components/canvas/RunOverlay";

interface BaseNodeProps {
  id: string;
  data: Record<string, unknown>;
  color?: string;
  children?: React.ReactNode;
}

export default function BaseNode({ id, data, color = "bg-slate-700", children }: BaseNodeProps) {
  const label = (data.label as string) ?? id;
  const stepType = (data.stepType as string) ?? "";

  return (
    <div className={`relative ${color} rounded-lg border border-slate-600 px-4 py-3 min-w-[160px]`}>
      <RunOverlay nodeId={id} />
      <Handle type="target" position={Position.Top} />
      <div className="text-xs text-slate-400 mb-1">{stepType}</div>
      <div className="text-sm font-medium">{label}</div>
      {children}
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}
