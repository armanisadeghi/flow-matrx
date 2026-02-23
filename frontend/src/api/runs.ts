import { apiClient } from "./client";
import type { Run } from "@shared/types/run";

export const runsApi = {
  listForWorkflow: (workflowId: string) =>
    apiClient.get<Run[]>(`/runs/workflow/${workflowId}`),
  get: (runId: string) => apiClient.get<Run>(`/runs/${runId}`),
  trigger: (workflowId: string, payload?: Record<string, unknown>) =>
    apiClient.post<{ run_id: string }>(`/runs/workflow/${workflowId}/trigger`, {
      trigger_payload: payload,
    }),
  cancel: (runId: string) => apiClient.post<void>(`/runs/${runId}/cancel`, {}),
  resume: (runId: string) => apiClient.post<void>(`/runs/${runId}/resume`, {}),
};
