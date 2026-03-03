import type { StepType } from "@shared/types/workflow";
import type { ComponentType } from "react";
import type { WorkflowNode } from "@shared/types/workflow";
import HttpRequestConfig from "./HttpRequestConfig";
import LLMCallConfig from "./LLMCallConfig";
import ConditionConfig from "./ConditionConfig";
import InlineCodeConfig from "./InlineCodeConfig";
import DatabaseQueryConfig from "./DatabaseQueryConfig";
import ApprovalConfig from "./ApprovalConfig";
import DelayConfig from "./DelayConfig";
import TransformConfig from "./TransformConfig";
import SendEmailConfig from "./SendEmailConfig";
import WebhookConfig from "./WebhookConfig";
import ForEachConfig from "./ForEachConfig";
import FunctionCallConfig from "./FunctionCallConfig";
import WaitForEventConfig from "./WaitForEventConfig";

interface ConfigProps {
  node: WorkflowNode;
}

export const configPanels: Partial<Record<StepType, ComponentType<ConfigProps>>> = {
  http_request: HttpRequestConfig,
  llm_call: LLMCallConfig,
  condition: ConditionConfig,
  inline_code: InlineCodeConfig,
  database_query: DatabaseQueryConfig,
  wait_for_approval: ApprovalConfig,
  delay: DelayConfig,
  transform: TransformConfig,
  send_email: SendEmailConfig,
  webhook: WebhookConfig,
  for_each: ForEachConfig,
  function_call: FunctionCallConfig,
  wait_for_event: WaitForEventConfig,
};
