import type { NodeTypes } from "@xyflow/react";
import HttpRequestNode from "./HttpRequestNode";
import LLMCallNode from "./LLMCallNode";
import ConditionNode from "./ConditionNode";
import InlineCodeNode from "./InlineCodeNode";
import DatabaseQueryNode from "./DatabaseQueryNode";
import ApprovalNode from "./ApprovalNode";
import DelayNode from "./DelayNode";
import TransformNode from "./TransformNode";
import SendEmailNode from "./SendEmailNode";
import WebhookNode from "./WebhookNode";
import ForEachNode from "./ForEachNode";
import FunctionCallNode from "./FunctionCallNode";
import WaitForEventNode from "./WaitForEventNode";

export const nodeTypes: NodeTypes = {
  http_request: HttpRequestNode,
  llm_call: LLMCallNode,
  condition: ConditionNode,
  inline_code: InlineCodeNode,
  database_query: DatabaseQueryNode,
  wait_for_approval: ApprovalNode,
  delay: DelayNode,
  transform: TransformNode,
  send_email: SendEmailNode,
  webhook: WebhookNode,
  for_each: ForEachNode,
  function_call: FunctionCallNode,
  wait_for_event: WaitForEventNode,
};
