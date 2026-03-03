import type { NodeProps } from "@xyflow/react";
import BaseNode from "./BaseNode";

export default function DatabaseQueryNode({ id, data }: NodeProps) {
  return <BaseNode id={id} data={data} color="bg-green-900" />;
}
