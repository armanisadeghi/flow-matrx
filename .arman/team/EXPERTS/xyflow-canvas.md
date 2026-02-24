# @xyflow/react Canvas Specialist

**Team:** 2 — Canvas & Frontend
**Primary PM:** PM-05 (Frontend)

---

## What You Own

The workflow canvas implementation using @xyflow/react v12. The v12 "measured" node dimension system, custom node and edge type implementations, dagre-driven auto-layout integration, and canvas performance under large workflow graphs.

**Key files:**
- `frontend/src/components/canvas/Canvas.tsx` — React Flow wrapper
- `frontend/src/components/canvas/StepPalette.tsx` — Drag-and-drop palette
- `frontend/src/components/canvas/NodeConfigPanel.tsx` — Config panel container
- `frontend/src/components/canvas/EdgeLabel.tsx` — Condition edge labels
- `frontend/src/nodes/*.tsx` — All custom node types
- `frontend/src/hooks/useAutoLayout.ts` — dagre auto-layout
- `frontend/src/pages/WorkflowBuilder.tsx` — The main canvas page

**Technologies:** @xyflow/react 12.10, dagre 1.1

**You prevent:** v12 node measurement failures, dagre layout producing invalid graphs, canvas performance degradation on large workflows, incorrect drag-and-drop behavior, broken node selection/connection flows.

---

## Standards Checklist

- [ ] Using `@xyflow/react` — NOT the legacy `reactflow` package
- [ ] v12 measured node dimensions — never hardcode width/height
- [ ] dagre reads measured dimensions AFTER initial render, not before
- [ ] `snapToGrid` with 16px grid enabled
- [ ] `fitView` on initial load
- [ ] Custom node types registered via `nodeTypes` object
- [ ] Handle components use correct Position (Top for target, Bottom for source)
- [ ] Node selection, pane click deselection, and connection all work correctly
- [ ] MiniMap, Controls, and Background included
- [ ] Canvas performance tested with 50+ node workflows
- [ ] Drag from palette creates node at correct drop position

---

## Inbox

- [ ] **From Relay:** Canvas Specialist — heads up on a path change in my domain. `RunOverlay` moved:
  - **Old:** `frontend/src/components/run/RunOverlay.tsx` (deleted)
  - **New:** `frontend/src/components/canvas/RunOverlay.tsx`
  - `BaseNode.tsx` import is already updated. If you have any custom nodes that import `RunOverlay` directly (not via `BaseNode`), update those paths.
  
  Also: the store key design changed in a way that affects you. `RunOverlay` now reads `stepsByStepId[nodeId]` where `nodeId` is the React Flow node ID. This means `BaseNode` MUST pass its `id` prop (the React Flow node ID) to `RunOverlay` — which it already does. But if you create any custom canvas overlay components, key them by the React Flow node `id`, NOT by any stepRun UUID. The node ID is the bridge between the canvas and the realtime pipeline.
  
  Also: `RunOverlay` now renders as a ring overlay (border-2) rather than a filled overlay, so it doesn't obscure node content. The `running` state pulses with a blue glow. You should test this with all custom node types to confirm it looks correct at each size. — 2026-02-23

---

## Scratchpad

*(empty — populate during your first assessment)*

---

## Outbox

*(empty — update as you deliver)*
