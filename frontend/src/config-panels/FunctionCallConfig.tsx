import type { WorkflowNode } from "@shared/types/workflow";
import { useWorkflowStore } from "../stores/workflowStore";
import CodeEditor from "../components/shared/CodeEditor";

interface ConfigProps {
  node: WorkflowNode;
}

export default function FunctionCallConfig({ node }: ConfigProps) {
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
        <span className="text-slate-400 block mb-1">Function Name</span>
        <input
          type="text"
          value={(node.config.function_name as string) ?? ""}
          onChange={(e) => update("function_name", e.target.value)}
          placeholder="my_custom_function"
          className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-sm"
        />
      </label>
      <label className="text-sm">
        <span className="text-slate-400 block mb-1">Arguments (JSON)</span>
        <CodeEditor
          value={(node.config.args as string) ?? "{}"}
          onChange={(v) => update("args", v)}
          language="json"
          height="150px"
        />
      </label>
    </div>
  );
}
