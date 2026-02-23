import type { NodeProps } from "@xyflow/react";
import BaseNode from "./BaseNode";

export default function ApprovalNode(props: NodeProps) {
  return <BaseNode {...props} color="bg-red-900" />;
}
