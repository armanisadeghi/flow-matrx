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

*(empty — waiting for first heartbeat)*

---

## Scratchpad

*(empty — populate during your first assessment)*

---

## Outbox

*(empty — update as you deliver)*
