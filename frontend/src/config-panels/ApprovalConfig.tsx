import type { WorkflowNode } from "@shared/types/workflow";
import { useWorkflowStore } from "../stores/workflowStore";

interface ConfigProps {
  node: WorkflowNode;
}

export default function ApprovalConfig({ node }: ConfigProps) {
  const { nodes, setNodes } = useWorkflowStore();
  const update = (key: string, value: unknown) =>
    setNodes(nodes.map((n) => (n.id === node.id ? { ...n, config: { ...n.config, [key]: value } } : n)));

  return (
    <div className="grid gap-3">
      <label className="text-sm">
        <span className="text-slate-400 block mb-1">Approval Prompt</span>
        <textarea
          value={(node.config.prompt as string) ?? "Please review and approve to continue."}
          onChange={(e) => update("prompt", e.target.value)}
          rows={4}
          className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-sm resize-none"
        />
      </label>
    </div>
  );
}
