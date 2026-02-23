import type { NodeProps } from "@xyflow/react";
import BaseNode from "./BaseNode";

export default function DatabaseQueryNode(props: NodeProps) {
  return <BaseNode {...props} color="bg-green-900" />;
}
