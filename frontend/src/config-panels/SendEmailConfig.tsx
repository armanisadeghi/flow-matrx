import type { WorkflowNode } from "@shared/types/workflow";
import TemplateInput from "../components/shared/TemplateInput";
import { useWorkflowStore } from "../stores/workflowStore";

interface ConfigProps {
  node: WorkflowNode;
}

export default function SendEmailConfig({ node }: ConfigProps) {
  const { nodes, setNodes } = useWorkflowStore();

  const update = (key: string, value: unknown) => {
    setNodes(
      nodes.map((n) =>
        n.id === node.id ? { ...n, config: { ...n.config, [key]: value } } : n,
      ),
    );
  };

  return (
    <div className="grid gap-3">
      <label className="text-sm">
        <span className="text-slate-400 block mb-1">To</span>
        <TemplateInput
          value={(node.config.to as string) ?? ""}
          onChange={(v) => update("to", v)}
          placeholder="recipient@example.com"
        />
      </label>
      <label className="text-sm">
        <span className="text-slate-400 block mb-1">Subject</span>
        <TemplateInput
          value={(node.config.subject as string) ?? ""}
          onChange={(v) => update("subject", v)}
          placeholder="Email subject..."
        />
      </label>
      <label className="text-sm">
        <span className="text-slate-400 block mb-1">Body</span>
        <textarea
          value={(node.config.body as string) ?? ""}
          onChange={(e) => update("body", e.target.value)}
          rows={4}
          placeholder="Email body..."
          className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-sm resize-none"
        />
      </label>
    </div>
  );
}
