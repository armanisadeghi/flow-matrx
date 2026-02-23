import type { NodeProps } from "@xyflow/react";
import BaseNode from "./BaseNode";

export default function HttpRequestNode(props: NodeProps) {
  return <BaseNode {...props} color="bg-blue-900" />;
}
