import type { NodeProps } from "@xyflow/react";
import BaseNode from "./BaseNode";

export default function LLMCallNode(props: NodeProps) {
  return <BaseNode {...props} color="bg-purple-900" />;
}
