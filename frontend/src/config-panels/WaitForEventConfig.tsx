import type { WorkflowNode } from "@shared/types/workflow";
import { useWorkflowStore } from "../stores/workflowStore";

interface ConfigProps {
  node: WorkflowNode;
}

export default function WaitForEventConfig({ node }: ConfigProps) {
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
        <span className="text-slate-400 block mb-1">Event Name</span>
        <input
          type="text"
          value={(node.config.event_name as string) ?? ""}
          onChange={(e) => update("event_name", e.target.value)}
          placeholder="user.approved"
          className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-sm"
        />
      </label>
      <label className="text-sm">
        <span className="text-slate-400 block mb-1">Timeout (seconds, optional)</span>
        <input
          type="number"
          value={(node.config.timeout_seconds as number) ?? ""}
          onChange={(e) => update("timeout_seconds", e.target.value ? Number(e.target.value) : null)}
          placeholder="No timeout"
          className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-sm"
        />
      </label>
    </div>
  );
}
