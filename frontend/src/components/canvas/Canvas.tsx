import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  type Connection,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useCallback, useEffect } from "react";
import { useWorkflowStore } from "../../stores/workflowStore";
import { nodeTypes } from "../../nodes";

export default function Canvas() {
  const { nodes: storeNodes, edges: storeEdges, setNodes, setEdges, setSelectedNode } =
    useWorkflowStore();

  const [nodes, , onNodesChange] = useNodesState(storeNodes as any[]);
  const [edges, , onEdgesChange] = useEdgesState(storeEdges as any[]);

  useEffect(() => {
    setNodes(nodes as any);
  }, [nodes, setNodes]);

  useEffect(() => {
    setEdges(edges as any);
  }, [edges, setEdges]);

  const onConnect = useCallback(
    (params: Connection) => {
      setEdges(addEdge(params, edges) as any);
    },
    [edges, setEdges]
  );

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      nodeTypes={nodeTypes}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
      onNodeClick={(_, node) => setSelectedNode(node.id)}
      fitView
    >
      <Background />
      <Controls />
      <MiniMap />
    </ReactFlow>
  );
}
