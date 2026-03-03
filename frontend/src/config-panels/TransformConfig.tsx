import type { WorkflowNode } from "@shared/types/workflow";
import { useWorkflowStore } from "../stores/workflowStore";
import CodeEditor from "../components/shared/CodeEditor";

interface ConfigProps {
  node: WorkflowNode;
}

export default function TransformConfig({ node }: ConfigProps) {
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
        <span className="text-slate-400 block mb-1">Mapping (JSON)</span>
        <CodeEditor
          value={(node.config.mapping as string) ?? "{}"}
          onChange={(v) => update("mapping", v)}
          language="json"
          height="200px"
        />
      </label>
    </div>
  );
}
