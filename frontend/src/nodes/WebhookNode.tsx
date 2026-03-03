import type { NodeProps } from "@xyflow/react";
import BaseNode from "./BaseNode";

export default function WebhookNode({ id, data }: NodeProps) {
  return <BaseNode id={id} data={data} color="bg-indigo-900" />;
}
