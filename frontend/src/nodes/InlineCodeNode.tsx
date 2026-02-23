import type { NodeProps } from "@xyflow/react";
import BaseNode from "./BaseNode";

export default function InlineCodeNode(props: NodeProps) {
  return <BaseNode {...props} color="bg-yellow-900" />;
}
