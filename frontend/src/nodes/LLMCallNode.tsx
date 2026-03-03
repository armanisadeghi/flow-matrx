import type { NodeProps } from "@xyflow/react";
import BaseNode from "./BaseNode";

export default function LLMCallNode({ id, data }: NodeProps) {
  return <BaseNode id={id} data={data} color="bg-purple-900" />;
}
