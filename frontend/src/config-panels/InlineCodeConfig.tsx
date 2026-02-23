import type { WorkflowNode } from "@shared/types/workflow";
import CodeEditor from "../components/shared/CodeEditor";
import { useWorkflowStore } from "../stores/workflowStore";

interface ConfigProps {
  node: WorkflowNode;
}

export default function InlineCodeConfig({ node }: ConfigProps) {
  const { nodes, setNodes } = useWorkflowStore();
  const update = (key: string, value: unknown) =>
    setNodes(nodes.map((n) => (n.id === node.id ? { ...n, config: { ...n.config, [key]: value } } : n)));

  return (
    <div className="grid gap-3">
      <span className="text-slate-400 text-sm">Python Code</span>
      <CodeEditor
        value={(node.config.code as string) ?? "# Write your code here\noutput = {}"}
        onChange={(v) => update("code", v)}
      />
    </div>
  );
}
