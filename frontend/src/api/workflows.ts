import { apiClient } from "./client";
import type { WorkflowDefinition } from "@shared/types/workflow";

export interface WorkflowSummary {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
}

export const workflowsApi = {
  list: () => apiClient.get<WorkflowSummary[]>("/workflows"),
  get: (id: string) => apiClient.get<WorkflowDefinition>(`/workflows/${id}`),
  create: (payload: { name: string; description?: string; definition: object }) =>
    apiClient.post<WorkflowDefinition>("/workflows", payload),
  update: (id: string, payload: { name: string; description?: string; definition: object }) =>
    apiClient.put<WorkflowDefinition>(`/workflows/${id}`, payload),
  delete: (id: string) => apiClient.delete(`/workflows/${id}`),
};
