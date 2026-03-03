import type { WorkflowNode } from "@shared/types/workflow";
import { useWorkflowStore } from "../stores/workflowStore";

interface ConfigProps {
  node: WorkflowNode;
}

export default function DelayConfig({ node }: ConfigProps) {
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
        <span className="text-slate-400 block mb-1">Duration (seconds)</span>
        <input
          type="number"
          value={(node.config.seconds as number) ?? 5}
          onChange={(e) => update("seconds", Number(e.target.value))}
          min={0}
          step={1}
          className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-sm"
        />
      </label>
    </div>
  );
}
