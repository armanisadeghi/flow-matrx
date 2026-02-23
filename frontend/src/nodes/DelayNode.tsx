import type { NodeProps } from "@xyflow/react";
import BaseNode from "./BaseNode";

export default function DelayNode(props: NodeProps) {
  return <BaseNode {...props} color="bg-slate-600" />;
}
