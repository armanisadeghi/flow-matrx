import type { NodeProps } from "@xyflow/react";
import BaseNode from "./BaseNode";

export default function ConditionNode({ id, data }: NodeProps) {
  return <BaseNode id={id} data={data} color="bg-orange-900" />;
}
