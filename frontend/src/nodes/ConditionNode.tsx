import type { NodeProps } from "@xyflow/react";
import BaseNode from "./BaseNode";

export default function ConditionNode(props: NodeProps) {
  return <BaseNode {...props} color="bg-orange-900" />;
}
