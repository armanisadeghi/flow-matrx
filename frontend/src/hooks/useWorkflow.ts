import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { workflowsApi } from "../api/workflows";

export function useWorkflowList() {
  return useQuery({ queryKey: ["workflows"], queryFn: workflowsApi.list });
}

export function useWorkflow(id: string | undefined) {
  return useQuery({
    queryKey: ["workflow", id],
    queryFn: () => workflowsApi.get(id!),
    enabled: !!id && id !== "new",
  });
}

export function useCreateWorkflow() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: workflowsApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["workflows"] }),
  });
}

export function useUpdateWorkflow(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Parameters<typeof workflowsApi.update>[1]) =>
      workflowsApi.update(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["workflow", id] });
      qc.invalidateQueries({ queryKey: ["workflows"] });
    },
  });
}
