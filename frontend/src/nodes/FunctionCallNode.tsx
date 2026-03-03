import type { NodeProps } from "@xyflow/react";
import BaseNode from "./BaseNode";

export default function FunctionCallNode({ id, data }: NodeProps) {
  return <BaseNode id={id} data={data} color="bg-violet-900" />;
}
