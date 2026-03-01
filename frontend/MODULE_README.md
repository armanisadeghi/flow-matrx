# frontend — Module Overview


## IMPORTANT: Do not edit auto-generated sections.

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `frontend` |
| Last generated | 2026-03-01 09:12 |
| Output file | `frontend/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py frontend --mode signatures
```

**To add permanent notes:** Write anywhere outside the `<!-- AUTO:... -->` blocks.
<!-- /AUTO:meta -->

<!-- HUMAN-EDITABLE: This section is yours. Agents & Humans can edit this section freely — it will not be overwritten. -->

## Architecture

> **Fill this in.** Describe the execution flow and layer map for this module.
> See `utils/code_context/MODULE_README_SPEC.md` for the recommended format.
>
> Suggested structure:
>
> ### Layers
> | File | Role |
> |------|------|
> | `entry.py` | Public entry point — receives requests, returns results |
> | `engine.py` | Core dispatch logic |
> | `models.py` | Shared data types |
>
> ### Call Flow (happy path)
> ```
> entry_function() → engine.dispatch() → implementation()
> ```


<!-- AUTO:tree -->
## Directory Tree

> Auto-generated. 51 files across 13 directories.

```
frontend/
├── MODULE_README.md
├── index.html
├── public/
├── src/
│   ├── App.tsx
│   ├── api/
│   │   ├── client.ts
│   │   ├── runs.ts
│   │   ├── workflows.ts
│   │   ├── ws.ts
│   ├── components/
│   │   ├── canvas/
│   │   │   ├── Canvas.tsx
│   │   │   ├── EdgeLabel.tsx
│   │   │   ├── NodeConfigPanel.tsx
│   │   │   ├── RunOverlay.tsx
│   │   │   ├── StepPalette.tsx
│   │   ├── run/
│   │   │   ├── ConnectionIndicator.tsx
│   │   │   ├── RunControls.tsx
│   │   │   ├── StepOutput.tsx
│   │   ├── shared/
│   │   │   ├── CodeEditor.tsx
│   │   │   ├── StatusBadge.tsx
│   │   │   ├── TemplateInput.tsx
│   ├── config-panels/
│   │   ├── ApprovalConfig.tsx
│   │   ├── ConditionConfig.tsx
│   │   ├── DatabaseQueryConfig.tsx
│   │   ├── HttpRequestConfig.tsx
│   │   ├── InlineCodeConfig.tsx
│   │   ├── LLMCallConfig.tsx
│   │   ├── index.ts
│   ├── hooks/
│   │   ├── useAutoLayout.ts
│   │   ├── useRunStream.ts
│   │   ├── useValidation.ts
│   │   ├── useWorkflow.ts
│   ├── lib/
│   │   ├── constants.ts
│   │   ├── graph-utils.ts
│   │   ├── templates.ts
│   │   ├── utils.ts
│   ├── main.tsx
│   ├── nodes/
│   │   ├── ApprovalNode.tsx
│   │   ├── BaseNode.tsx
│   │   ├── ConditionNode.tsx
│   │   ├── DatabaseQueryNode.tsx
│   │   ├── DelayNode.tsx
│   │   ├── HttpRequestNode.tsx
│   │   ├── InlineCodeNode.tsx
│   │   ├── LLMCallNode.tsx
│   │   ├── index.ts
│   ├── pages/
│   │   ├── RunDetail.tsx
│   │   ├── RunHistory.tsx
│   │   ├── WorkflowBuilder.tsx
│   │   ├── WorkflowList.tsx
│   ├── stores/
│   │   ├── runStore.ts
│   │   ├── workflowStore.ts
│   ├── types/
│   │   ├── index.ts
├── vite.config.ts
# excluded: 5 .json, 2 .yaml, 1 .md, 1 .css, 1 .svg
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: frontend/vite.config.ts  [typescript]



---
Filepath: frontend/index.html  [unknown (.html)]

  # signature extraction not supported for this language


---
Filepath: frontend/src/main.tsx  [typescript]



---
Filepath: frontend/src/App.tsx  [typescript]

  return ( <BrowserRouter> <Routes> <Route path="/" element={<WorkflowList />} /> <Route path="/workflows/:workflowId/edit" element={<WorkflowBuilder />} /> <Route path="/workflows/:workflowId/runs" element={<RunHistory />} /> <Route path="/runs/:runId" element={<RunDetail />} /> </Routes> </BrowserRouter> )


---
Filepath: frontend/src/api/runs.ts  [typescript]



---
Filepath: frontend/src/api/workflows.ts  [typescript]

  export interface WorkflowSummary


---
Filepath: frontend/src/api/ws.ts  [typescript]

  export type EventHandler = (event: WorkflowEvent) => void
  export type ConnectionStateHandler = (connected: boolean, attempt: number) => void
  export interface RunWebSocketHandle
  function backoffDelay(attempt: number): number
  export function createRunWebSocket( runId: string, onEvent: EventHandler, onConnectionState: ConnectionStateHandler, ): RunWebSocketHandle
  onConnectionState(true, 0)
  onEvent(event)
  onConnectionState(false, attempt)
  if (attempt >= MAX_RETRIES)
  connect()
  close()


---
Filepath: frontend/src/api/client.ts  [typescript]

  async function request<T>(path: string, init?: RequestInit): Promise<T>
  if (!response.ok)


---
Filepath: frontend/src/types/index.ts  [typescript]



---
Filepath: frontend/src/config-panels/DatabaseQueryConfig.tsx  [typescript]

  interface ConfigProps


---
Filepath: frontend/src/config-panels/LLMCallConfig.tsx  [typescript]

  interface ConfigProps


---
Filepath: frontend/src/config-panels/InlineCodeConfig.tsx  [typescript]

  interface ConfigProps


---
Filepath: frontend/src/config-panels/ApprovalConfig.tsx  [typescript]

  interface ConfigProps


---
Filepath: frontend/src/config-panels/ConditionConfig.tsx  [typescript]

  interface ConfigProps


---
Filepath: frontend/src/config-panels/HttpRequestConfig.tsx  [typescript]

  interface ConfigProps


---
Filepath: frontend/src/config-panels/index.ts  [typescript]

  interface ConfigProps


---
Filepath: frontend/src/components/shared/TemplateInput.tsx  [typescript]

  interface TemplateInputProps


---
Filepath: frontend/src/components/shared/CodeEditor.tsx  [typescript]

  interface CodeEditorProps


---
Filepath: frontend/src/components/shared/StatusBadge.tsx  [typescript]

  type Status = RunStatus | StepRunStatus
  interface StatusBadgeProps


---
Filepath: frontend/src/components/run/ConnectionIndicator.tsx  [typescript]

  interface ConnectionIndicatorProps


---
Filepath: frontend/src/components/run/StepOutput.tsx  [typescript]

  interface StepOutputProps


---
Filepath: frontend/src/components/run/RunControls.tsx  [typescript]

  interface RunControlsProps


---
Filepath: frontend/src/components/canvas/StepPalette.tsx  [typescript]



---
Filepath: frontend/src/components/canvas/EdgeLabel.tsx  [typescript]

  interface EdgeLabelProps


---
Filepath: frontend/src/components/canvas/Canvas.tsx  [typescript]

  useWorkflowStore()
  setNodes(nodes as any)
  setEdges(edges as any)


---
Filepath: frontend/src/components/canvas/NodeConfigPanel.tsx  [typescript]

  if (!node)
  return ( <div className="w-72 border-l border-slate-700 bg-slate-800 p-4 flex items-center justify-center"> <p className="text-slate-500 text-sm">Select a node to configure</p> </div> )
  return ( <div className="w-72 border-l border-slate-700 bg-slate-800 p-4 overflow-y-auto"> <h2 className="font-semibold mb-4">{node.label}</h2> {ConfigPanel ? ( <ConfigPanel node={node} /> ) : ( <p className="text-slate-500 text-sm">No config panel for


---
Filepath: frontend/src/components/canvas/RunOverlay.tsx  [typescript]

  interface RunOverlayProps
  return ( <div className={`absolute inset-0 rounded-lg border-2 pointer-events-none transition-all duration-300 ${STATUS_RING[step.status]}`} /> )


---
Filepath: frontend/src/nodes/HttpRequestNode.tsx  [typescript]



---
Filepath: frontend/src/nodes/index.ts  [typescript]



---
Filepath: frontend/src/nodes/DatabaseQueryNode.tsx  [typescript]



---
Filepath: frontend/src/nodes/ConditionNode.tsx  [typescript]



---
Filepath: frontend/src/nodes/InlineCodeNode.tsx  [typescript]



---
Filepath: frontend/src/nodes/DelayNode.tsx  [typescript]



---
Filepath: frontend/src/nodes/BaseNode.tsx  [typescript]

  interface BaseNodeData
  interface BaseNodeProps extends NodeProps
  return ( <div className={`relative ${color} rounded-lg border border-slate-600 px-4 py-3 min-w-[160px]`}> <RunOverlay nodeId={id} /> <Handle type="target" position={Position.Top} /> <div className="text-xs text-slate-400 mb-1">{data.stepType}</div> <div className="text-sm font-medium">{data.label}</div> {children} <Handle type="source" position={Position.Bottom} /> </div> )


---
Filepath: frontend/src/nodes/ApprovalNode.tsx  [typescript]



---
Filepath: frontend/src/nodes/LLMCallNode.tsx  [typescript]



---
Filepath: frontend/src/pages/RunDetail.tsx  [typescript]

  useRunStream(runId ?? null)
  if (!initialRun && !activeRunId)
  return ( <div className="p-8"> <div className="flex items-center justify-between mb-6"> <div> <h1 className="text-2xl font-bold">Run Detail</h1> <p className="font-mono text-sm text-slate-400">{displayRunId}</p> </div> <div className="flex items-center gap-4"> <ConnectionIndicator connected={connected} /> <StatusBadge status={displayStatus} /> <RunControls runId={displayRunId} status={displayStatus} /> </div> </div> {steps.length === 0 ? ( <p className="text-slate-500 text-sm">Waiting for steps to begin...</p> ) : ( <div className="grid gap-4">


---
Filepath: frontend/src/pages/WorkflowBuilder.tsx  [typescript]

  if (workflow)
  setWorkflow(workflow.id, workflow.name, workflow.nodes, workflow.edges)
  return ( <div className="flex h-screen"> <StepPalette /> <div className="flex-1"> <Canvas /> </div> <NodeConfigPanel /> </div> )


---
Filepath: frontend/src/pages/WorkflowList.tsx  [typescript]

  if (isLoading)


---
Filepath: frontend/src/pages/RunHistory.tsx  [typescript]



---
Filepath: frontend/src/lib/graph-utils.ts  [typescript]

  export function getUpstream(nodeId: string, edges: WorkflowEdge[]): string[]
  export function getDownstream(nodeId: string, edges: WorkflowEdge[]): string[]
  export function getRootNodes(nodes: WorkflowNode[], edges: WorkflowEdge[]): WorkflowNode[]


---
Filepath: frontend/src/lib/templates.ts  [typescript]

  export interface TemplateRef
  export function parseTemplateRefs(value: string): TemplateRef[]
  export function hasTemplateRefs(value: string): boolean


---
Filepath: frontend/src/lib/utils.ts  [typescript]

  export function cn(...inputs: ClassValue[])


---
Filepath: frontend/src/lib/constants.ts  [typescript]



---
Filepath: frontend/src/stores/runStore.ts  [typescript]

  export interface StepState
  interface RunStore


---
Filepath: frontend/src/stores/workflowStore.ts  [typescript]

  interface WorkflowState


---
Filepath: frontend/src/hooks/useAutoLayout.ts  [typescript]

  export function useAutoLayout()
  setNodes(layouted)


---
Filepath: frontend/src/hooks/useWorkflow.ts  [typescript]

  export function useWorkflowList()
  export function useWorkflow(id: string | undefined)
  export function useCreateWorkflow()
  export function useUpdateWorkflow(id: string)


---
Filepath: frontend/src/hooks/useValidation.ts  [typescript]

  interface ValidationError
  export function useValidation(): ValidationError[]
  for (const edge of edges)


---
Filepath: frontend/src/hooks/useRunStream.ts  [typescript]

  function handleSnapshot(event: SnapshotEvent): void
  function handleRunStatus(event: RunStatusEvent): void
  function handleStepStatus(event: StepStatusEvent): void
  function handleContextUpdated(event: ContextUpdatedEvent): void
  function dispatch(event: WorkflowEvent): void
  export function useRunStream(runId: string | null): void
  setStepStatus(event.step_id, status, { attempt: event.payload.attempt, output: event.payload.output, error: event.payload.error, })
  switch (event.type)
  handleSnapshot(event)
  handleRunStatus(event as RunStatusEvent)
  handleStepStatus(event as StepStatusEvent)
  handleContextUpdated(event as ContextUpdatedEvent)
  setConnected(connected)
  setReconnectAttempt(attempt)
  setConnected(false)
```
<!-- /AUTO:signatures -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "frontend",
  "mode": "signatures",
  "scope": null,
  "project_noise": null,
  "include_call_graph": false,
  "entry_points": null,
  "call_graph_exclude": [
    "tests"
  ],
  "signatures_exclude": [
    "tests"
  ]
}
```
<!-- /AUTO:config -->
