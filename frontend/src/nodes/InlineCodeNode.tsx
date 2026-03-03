import type { NodeProps } from "@xyflow/react";
import BaseNode from "./BaseNode";

export default function InlineCodeNode({ id, data }: NodeProps) {
  return <BaseNode id={id} data={data} color="bg-yellow-900" />;
}
