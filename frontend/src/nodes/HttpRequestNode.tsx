import type { NodeProps } from "@xyflow/react";
import BaseNode from "./BaseNode";

export default function HttpRequestNode({ id, data }: NodeProps) {
  return <BaseNode id={id} data={data} color="bg-blue-900" />;
}
