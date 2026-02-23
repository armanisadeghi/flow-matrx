import { Handle, Position, type NodeProps } from "@xyflow/react";
import RunOverlay from "../components/run/RunOverlay";

interface BaseNodeData {
  label: string;
  stepType: string;
}

interface BaseNodeProps extends NodeProps {
  data: BaseNodeData;
  color?: string;
  children?: React.ReactNode;
}

export default function BaseNode({ id, data, color = "bg-slate-700", children }: BaseNodeProps) {
  return (
    <div className={`relative ${color} rounded-lg border border-slate-600 px-4 py-3 min-w-[160px]`}>
      <RunOverlay nodeId={id} />
      <Handle type="target" position={Position.Top} />
      <div className="text-xs text-slate-400 mb-1">{data.stepType}</div>
      <div className="text-sm font-medium">{data.label}</div>
      {children}
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}
