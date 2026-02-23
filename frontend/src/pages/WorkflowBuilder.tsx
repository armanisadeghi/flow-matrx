import { useParams } from "react-router";
import { useQuery } from "@tanstack/react-query";
import { workflowsApi } from "../api/workflows";
import Canvas from "../components/canvas/Canvas";
import StepPalette from "../components/canvas/StepPalette";
import NodeConfigPanel from "../components/canvas/NodeConfigPanel";
import { useWorkflowStore } from "../stores/workflowStore";
import { useEffect } from "react";

export default function WorkflowBuilder() {
  const { workflowId } = useParams<{ workflowId: string }>();
  const setWorkflow = useWorkflowStore((s) => s.setWorkflow);

  const { data: workflow } = useQuery({
    queryKey: ["workflow", workflowId],
    queryFn: () => workflowsApi.get(workflowId!),
    enabled: !!workflowId && workflowId !== "new",
  });

  useEffect(() => {
    if (workflow) {
      setWorkflow(workflow.id, workflow.name, workflow.nodes, workflow.edges);
    }
  }, [workflow, setWorkflow]);

  return (
    <div className="flex h-screen">
      <StepPalette />
      <div className="flex-1">
        <Canvas />
      </div>
      <NodeConfigPanel />
    </div>
  );
}
