import { useWorkflowStore } from "../../stores/workflowStore";
import { configPanels } from "../../config-panels";
import type { StepType } from "@shared/types/workflow";

export default function NodeConfigPanel() {
  const { selectedNodeId, nodes } = useWorkflowStore();
  const node = nodes.find((n) => n.id === selectedNodeId);

  if (!node) {
    return (
      <div className="w-72 border-l border-slate-700 bg-slate-800 p-4 flex items-center justify-center">
        <p className="text-slate-500 text-sm">Select a node to configure</p>
      </div>
    );
  }

  const ConfigPanel = configPanels[node.type as StepType];

  return (
    <div className="w-72 border-l border-slate-700 bg-slate-800 p-4 overflow-y-auto">
      <h2 className="font-semibold mb-4">{node.label}</h2>
      {ConfigPanel ? (
        <ConfigPanel node={node} />
      ) : (
        <p className="text-slate-500 text-sm">No config panel for {node.type}</p>
      )}
    </div>
  );
}
