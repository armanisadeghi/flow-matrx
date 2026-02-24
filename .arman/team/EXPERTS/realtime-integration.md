# Realtime Integration Specialist

**Codename:** Relay
**Team:** 4 — API Integration & Security
**Primary PM:** PM-04 (API Layer)
**Secondary PMs:** PM-02 (Execution Engine), PM-05 (Frontend)

---

## What You Own

The complete realtime pipeline: engine event emission → Event Bus → WebSocket transport → frontend store update. This cross-boundary pipeline is the highest integration-complexity point in the system.

**Key files:**
- `backend/app/events/bus.py` — Event Bus (in-process pub/sub)
- `backend/app/events/types.py` — Event type definitions
- `backend/app/api/ws.py` — WebSocket endpoint
- `frontend/src/api/ws.ts` — WebSocket connection manager (reconnection logic)
- `frontend/src/hooks/useRunStream.ts` — Event dispatch + store integration
- `frontend/src/stores/runStore.ts` — Live run state (the single truth for UI)
- `packages/shared/types/events.ts` — Shared event type contracts

**Technologies:** asyncio.Queue, FastAPI WebSocket, browser WebSocket API, Zustand

**You prevent:** Execution status never reaching the frontend, PubSub channel leaks, snapshot-on-connect failures, event ordering issues, WebSocket reconnection data loss.

---

## Standards Checklist

- [x] Event Bus persists EVERY event to run_events table AND broadcasts to subscribers
- [x] WebSocket sends snapshot on connect — non-negotiable for late joiners
- [x] Snapshot contains current status of ALL step_runs for the run
- [x] Live events stream in order after snapshot
- [x] WebSocket disconnect triggers proper unsubscribe (no leaking queues)
- [x] Frontend `useRunStream` handles snapshot → `loadSnapshot()` correctly
- [x] Frontend routes step events to `setStepStatus()` and run events to `setRunStatus()`
- [x] Connection state tracked via `setConnected()`
- [x] Reconnection is graceful — new snapshot sent, no duplicated events (idempotent writes)
- [x] Event payloads match the documented shapes in the spec exactly
- [x] No polling anywhere in the realtime pipeline
- [ ] WebSocket tests: connect + snapshot, live event routing, reconnection, disconnect cleanup

---

## Inbox

*(cleared — all items actioned this heartbeat)*

---

## Scratchpad

### Second Heartbeat — 2026-02-23

**What Axiom/Pulse did while I was away (already landed, all good):**
- `bus.py`: Now persists every event to `run_events` before broadcasting. Also cleans up empty subscriber maps on unsubscribe. Queue is bounded at 256, drops on full with a warning log.
- `types.py`: Now a `StrEnum` with all 13 types, including the 4 I flagged as missing.
- `ws.py`: Subscribe-before-snapshot (Pulse), proper snapshot query (Axiom), maxsize=256 queue, finally-block cleanup.

**What I shipped this heartbeat:**

1. **`packages/shared/types/events.ts` — Complete rewrite**
   - Added `SnapshotEvent` type with exact shape matching `ws.py`'s output
   - Added `RunStatusEvent` with all 6 run states
   - Added `StepStatusEvent` with all 6 step states
   - Added `ContextUpdatedEvent`
   - `WorkflowEvent` = union of all of the above
   - Removed the old partial/incorrect types (stale `ApprovalRequiredEvent` etc.)

2. **`frontend/src/stores/runStore.ts` — Full rebuild**
   - New `StepState` type: keyed by `step_id` (React Flow node ID), not stepRun UUID — this is the critical decision that makes `RunOverlay` work correctly
   - Added: `connected`, `reconnectAttempt`, `activeRunId`, `runStatus`, `context`
   - Added: `setConnected`, `setReconnectAttempt`, `loadSnapshot`, `setRunStatus`, `setStepStatus`, `setContext`
   - `setStepStatus` is idempotent — repeated calls with same status don't re-render (Zustand shallow equality)

3. **`frontend/src/api/ws.ts` — Reconnection manager**
   - Exponential backoff: 500ms * 2^attempt + jitter, capped at 30s
   - Max 8 retries before giving up
   - `destroyed` flag prevents reconnect after intentional close
   - Returns `RunWebSocketHandle` with `close()` — clean lifecycle
   - `onConnectionState(connected, attempt)` callback drives the store

4. **`frontend/src/hooks/useRunStream.ts` — Full rewrite**
   - Module-level `dispatch()` function — stable reference, no recreation on re-render
   - Handles all 13 event types via exhaustive switch
   - `EVENT_TYPE_TO_STATUS` map derives StepRunStatus from event type for events that don't carry it in payload (e.g. `step.started` → `"running"`)
   - Dedup is idempotent — snapshot + live event for same step = no duplicate render

5. **`frontend/src/pages/RunDetail.tsx` — Cache/store split pattern**
   - `useQuery` fires once with `staleTime: Infinity` to get run metadata
   - `useRunStream` drives all live state into the store
   - All rendered values read from Zustand store
   - Resets store on unmount
   - This answers Cache's question — see my reply in his inbox

6. **`frontend/src/components/run/StepOutput.tsx` — Updated to `StepState`**
   - Shows step type badge, attempt number on retry, output JSON, error string

7. **`frontend/src/components/run/RunControls.tsx` — Fixed**
   - Now takes `runId` + `status` as props (from store, not from stale REST run object)
   - Invalidates `["run", runId]` and `["runs"]` query keys after cancel

8. **`frontend/src/components/run/ConnectionIndicator.tsx` — New component**
   - Green glowing dot when live, grey dot with "connecting..." when not
   - Appears in RunDetail header

9. **`frontend/src/components/canvas/RunOverlay.tsx` — Moved + improved**
   - Now reads from `stepsByStepId[nodeId]` (keyed by node ID)
   - Ring-style overlay with status-specific colors + animation for `running`
   - Moved to `components/canvas/` where it belongs
   - Old `components/run/RunOverlay.tsx` deleted
   - `BaseNode.tsx` import path updated

**Key architectural decision recorded:**

Store keys step state by `step_id` (React Flow node ID), not by `stepRun.id` (UUID). This is the only design that makes `RunOverlay` (canvas node decoration) work without an additional lookup. When the engine calls `event_bus.emit(run_id, STEP_STARTED, step_id=node_id, ...)`, the `step_id` is the React Flow node ID, which is the same ID `BaseNode` passes to `RunOverlay`. This is correct and intentional.

**What remains unblocked for next heartbeat:**

- WebSocket tests (D9 in PM-04) — connect + snapshot, event routing, reconnect, disconnect cleanup
- Leave note for Canvas Specialist about the `RunOverlay` move (path changed)
- Watch for context.updated — currently `setContext` replaces the whole context dict. May need to merge instead if engine sends partial updates. Need to check executor — yes, executor sends full context on CONTEXT_UPDATED (`context=context` from `run_mgr.update_item`). Full replace is correct.
- Arman mentioned "highly structured data with known types" — the event shape I've designed does this. Each event type has a discriminated union in TypeScript. Next: consider adding a `meta` field to events for timing/tracing info that the UI can surface (step duration, queue depth, etc.) — leave this as a proposal for Arman.

**What Cache and I agreed on (coordination decision):**
- Initial `useQuery` on RunDetail with `staleTime: Infinity` bootstraps the page shell
- Store is populated by WebSocket snapshot on connect
- All live renders read from store exclusively
- `queryClient.invalidateQueries` called after terminal actions (cancel, complete) so RunHistory picks up final state

---

## Outbox

- [x] **Rebuilt `packages/shared/types/events.ts`** — complete type coverage for all 13 event types + snapshot shape — 2026-02-23
- [x] **Rebuilt `frontend/src/stores/runStore.ts`** — connection state, run status, step state by node ID, snapshot loader — 2026-02-23
- [x] **Rebuilt `frontend/src/api/ws.ts`** — exponential backoff reconnection, clean lifecycle — 2026-02-23
- [x] **Rebuilt `frontend/src/hooks/useRunStream.ts`** — all 13 event types, snapshot handling, idempotent step state — 2026-02-23
- [x] **Fixed `frontend/src/pages/RunDetail.tsx`** — store-first rendering, stale cache problem eliminated — 2026-02-23
- [x] **New `frontend/src/components/run/ConnectionIndicator.tsx`** — live connection status visible in UI — 2026-02-23
- [x] **New `frontend/src/components/canvas/RunOverlay.tsx`** — improved node status ring, moved to canvas folder — 2026-02-23
- [x] **Updated `frontend/src/components/run/StepOutput.tsx`** — uses StepState, shows type badge + attempt count — 2026-02-23
- [x] **Fixed `frontend/src/components/run/RunControls.tsx`** — reads status from store, not stale REST response — 2026-02-23
- [!] **FLAG for Canvas Specialist:** `RunOverlay` moved from `components/run/` to `components/canvas/`. `BaseNode.tsx` import path updated. If you have any custom nodes that import directly from `components/run/RunOverlay`, update those imports. — 2026-02-23
