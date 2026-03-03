import type { NodeProps } from "@xyflow/react";
import BaseNode from "./BaseNode";

export default function ApprovalNode({ id, data }: NodeProps) {
  return <BaseNode id={id} data={data} color="bg-red-900" />;
}
