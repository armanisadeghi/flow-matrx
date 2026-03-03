import type { NodeProps } from "@xyflow/react";
import BaseNode from "./BaseNode";

export default function SendEmailNode({ id, data }: NodeProps) {
  return <BaseNode id={id} data={data} color="bg-teal-900" />;
}
