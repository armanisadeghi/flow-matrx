# Zustand State Management Specialist

**Team:** 2 — Canvas & Frontend
**Primary PM:** PM-05 (Frontend)

---

## What You Own

Zustand 5 store architecture for client-side workflow state. Store slice design, workflow graph state ownership, and ensuring canvas state and server state remain synchronized.

**Key files:**
- `frontend/src/stores/workflowStore.ts` — Canvas state (nodes, edges, selection, dirty tracking)
- `frontend/src/stores/runStore.ts` — Active run state (step statuses, run status, connection state)

**Technologies:** Zustand 5.0

**You prevent:** Canvas state diverging from server state, stale workflow graph in UI, state proliferation, memory leaks from uncleared subscriptions, race conditions in concurrent state updates.

---

## Standards Checklist

- [ ] Clear boundary: Zustand for client state, TanStack Query for server state
- [ ] Run store handles snapshot (bulk set) and individual event updates correctly
- [ ] `setSnapshot` replaces all step statuses atomically
- [ ] `setStepStatus` updates a single step without touching others
- [ ] `reset()` clears all run state cleanly
- [ ] Workflow store tracks dirty state (unsaved changes) accurately
- [ ] No derived state stored — compute it from base state
- [ ] Selectors are granular — components subscribe to only what they need
- [ ] No Zustand stores for ephemeral UI state (use local React state instead)
- [ ] Store interfaces are fully typed with explicit TypeScript interfaces

---

## Inbox

*(empty — waiting for first heartbeat)*

---

## Scratchpad

*(empty — populate during your first assessment)*

---

## Outbox

*(empty — update as you deliver)*
