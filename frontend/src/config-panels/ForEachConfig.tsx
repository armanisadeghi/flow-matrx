import type { WorkflowNode } from "@shared/types/workflow";
import TemplateInput from "../components/shared/TemplateInput";
import { useWorkflowStore } from "../stores/workflowStore";

interface ConfigProps {
  node: WorkflowNode;
}

export default function ForEachConfig({ node }: ConfigProps) {
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
        <span className="text-slate-400 block mb-1">Items (template expression)</span>
        <TemplateInput
          value={(node.config.items as string) ?? ""}
          onChange={(v) => update("items", v)}
          placeholder="{{step_id.results}}"
        />
      </label>
      <label className="text-sm">
        <span className="text-slate-400 block mb-1">Handler Step Type</span>
        <input
          type="text"
          value={(node.config.handler as string) ?? ""}
          onChange={(e) => update("handler", e.target.value)}
          placeholder="transform"
          className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-sm"
        />
      </label>
      <label className="text-sm flex items-center gap-2">
        <input
          type="checkbox"
          checked={(node.config.parallel as boolean) ?? false}
          onChange={(e) => update("parallel", e.target.checked)}
          className="rounded border-slate-600"
        />
        <span className="text-slate-400">Run iterations in parallel</span>
      </label>
    </div>
  );
}
