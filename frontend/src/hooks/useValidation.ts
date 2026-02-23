import { useMemo } from "react";
import { useWorkflowStore } from "../stores/workflowStore";

interface ValidationError {
  nodeId?: string;
  message: string;
}

export function useValidation(): ValidationError[] {
  const { nodes, edges } = useWorkflowStore();

  return useMemo(() => {
    const errors: ValidationError[] = [];
    const nodeIds = new Set(nodes.map((n) => n.id));

    for (const edge of edges) {
      if (!nodeIds.has(edge.source)) {
        errors.push({ message: `Edge source ${edge.source} does not exist` });
      }
      if (!nodeIds.has(edge.target)) {
        errors.push({ message: `Edge target ${edge.target} does not exist` });
      }
    }

    return errors;
  }, [nodes, edges]);
}
