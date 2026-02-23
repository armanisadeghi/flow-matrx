import type { WorkflowNode } from "@shared/types/workflow";
import TemplateInput from "../components/shared/TemplateInput";
import { useWorkflowStore } from "../stores/workflowStore";

interface ConfigProps {
  node: WorkflowNode;
}

export default function HttpRequestConfig({ node }: ConfigProps) {
  const { nodes, setNodes } = useWorkflowStore();

  const update = (key: string, value: unknown) => {
    setNodes(
      nodes.map((n) =>
        n.id === node.id ? { ...n, config: { ...n.config, [key]: value } } : n
      )
    );
  };

  return (
    <div className="grid gap-3">
      <label className="text-sm">
        <span className="text-slate-400 block mb-1">Method</span>
        <select
          value={(node.config.method as string) ?? "GET"}
          onChange={(e) => update("method", e.target.value)}
          className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-sm"
        >
          {["GET", "POST", "PUT", "PATCH", "DELETE"].map((m) => (
            <option key={m}>{m}</option>
          ))}
        </select>
      </label>
      <label className="text-sm">
        <span className="text-slate-400 block mb-1">URL</span>
        <TemplateInput
          value={(node.config.url as string) ?? ""}
          onChange={(v) => update("url", v)}
          placeholder="https://api.example.com/..."
        />
      </label>
    </div>
  );
}
