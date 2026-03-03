import type { NodeProps } from "@xyflow/react";
import BaseNode from "./BaseNode";

export default function ForEachNode({ id, data }: NodeProps) {
  return <BaseNode id={id} data={data} color="bg-emerald-900" />;
}
