import type { NodeProps } from "@xyflow/react";
import BaseNode from "./BaseNode";

export default function WaitForEventNode({ id, data }: NodeProps) {
  return <BaseNode id={id} data={data} color="bg-pink-900" />;
}
