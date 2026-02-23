import type { WorkflowNode } from "@shared/types/workflow";
import TemplateInput from "../components/shared/TemplateInput";
import { useWorkflowStore } from "../stores/workflowStore";

interface ConfigProps {
  node: WorkflowNode;
}

export default function ConditionConfig({ node }: ConfigProps) {
  const { nodes, setNodes } = useWorkflowStore();
  const update = (key: string, value: unknown) =>
    setNodes(nodes.map((n) => (n.id === node.id ? { ...n, config: { ...n.config, [key]: value } } : n)));

  return (
    <div className="grid gap-3">
      <label className="text-sm">
        <span className="text-slate-400 block mb-1">Expression</span>
        <TemplateInput
          value={(node.config.expression as string) ?? ""}
          onChange={(v) => update("expression", v)}
          placeholder="step1.result == true"
        />
      </label>
    </div>
  );
}
