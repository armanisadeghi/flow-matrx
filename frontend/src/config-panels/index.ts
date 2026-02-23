import type { StepType } from "@shared/types/workflow";
import type { ComponentType } from "react";
import type { WorkflowNode } from "@shared/types/workflow";
import HttpRequestConfig from "./HttpRequestConfig";
import LLMCallConfig from "./LLMCallConfig";
import ConditionConfig from "./ConditionConfig";
import InlineCodeConfig from "./InlineCodeConfig";
import DatabaseQueryConfig from "./DatabaseQueryConfig";
import ApprovalConfig from "./ApprovalConfig";

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
};
