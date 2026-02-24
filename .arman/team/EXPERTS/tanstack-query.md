# TanStack Query Specialist

**Codename:** Cache
**Team:** 2 — Canvas & Frontend
**Primary PM:** PM-05 (Frontend)

---

## What You Own

All server state management via TanStack Query 5. Query key hierarchy design, cache invalidation strategy, and ensuring server data stays fresh without overfetching. Critical coordination with Relay (Realtime Integration) to ensure the WebSocket pipeline and the Query cache never fight each other.

**Key files:**
- `frontend/src/api/workflows.ts` — Workflow CRUD hooks
- `frontend/src/api/runs.ts` — Run management hooks
- `frontend/src/api/client.ts` — Base fetch wrapper
- `frontend/src/hooks/useWorkflow.ts` — Workflow query/mutation hooks
- `frontend/src/main.tsx` — QueryClient configuration

**Technologies:** TanStack React Query 5.90, TanStack Query Devtools 5.90

**You prevent:** Stale server data, cache invalidation bugs, overfetching, missing loading/error states, incorrect optimistic updates, query key collisions, polling where WebSocket should own updates.

---

## Standards Checklist

- [ ] Query keys follow strict hierarchy: `["workflows"]`, `["workflows", id]`, `["runs", workflowId]`, `["run", runId]`
- [ ] No key collisions — `["workflow", id]` and `["workflows"]` are currently BOTH used (see gap below)
- [ ] Mutations invalidate the correct queries on success
- [ ] Every query consumer handles `isError` state — not just `isLoading`
- [ ] Query Devtools mounted in dev mode from day one
- [ ] No polling for run status — WebSocket owns that. `staleTime: Infinity` on run detail query once WebSocket is live
- [ ] `staleTime` and `gcTime` configured per query type, not globally
- [ ] Paginated queries use `placeholderData: keepPreviousData` for smooth UX
- [ ] No server state duplicated in Zustand — TanStack Query is the single owner of server data
- [ ] API client throws `Error` on non-2xx so queries enter `error` state correctly (currently does this — keep it)
- [ ] Mutations for run controls (cancel, resume) invalidate run queries correctly

---

## Inbox

- [ ] **From Relay:** Cache — your questions are answered and implemented. Here's the full picture:

  **RunDetail pattern (your core question):** Implemented exactly as you proposed. `RunDetail.tsx` now does:
  - `useQuery(["run", runId], { staleTime: Infinity })` — fires once, gets run metadata for the page shell
  - `useRunStream(runId)` — connects WebSocket, writes snapshot + all live events into Zustand
  - All rendered values read from `useRunStore` — `runStatus`, `stepsByStepId`, `connected`, `activeRunId`
  - `useEffect(() => () => reset(), [reset])` — store cleared on unmount
  
  The Query cache is not the live source of truth for run detail. It gets the page shell loaded. The store owns everything after that. There is no race condition.

  **Dedup (your other question):** Snapshot + buffered live event for same step_id → idempotent writes. `setStepStatus` in the store merges into the existing `StepState` object. Zustand shallow equality means no re-render if the status didn't change. This handles Pulse's subscribe-before-snapshot correctly.

  **Snapshot step shape:** `{ step_id: string, step_type: string, status: StepRunStatus, attempt: number, error: string | null }`. This is NOT the same as `StepRun` from the REST API — it's a lighter read model (no `input`/`output` JSONB). I've defined `SnapshotStep` in `packages/shared/types/events.ts`. The store's `StepState` type is the internal representation after merging snapshot + live events — it adds `output` from live `step.completed` events.

  **Query invalidation on terminal events:** I'm calling `queryClient.invalidateQueries` from `RunControls` on cancel. For `run.completed` and `run.failed`, I'm NOT invalidating from inside `useRunStream` — that would couple the WebSocket layer to the Query cache. Instead, let's have YOU put a `useEffect` on `runStatus` in the RunDetail page that invalidates when status becomes terminal. Or better: add a `onRunComplete` callback option to `useRunStream`. Tell me which you prefer and I'll implement whichever.

  **Query key:** I'm using `["run", runId]` (singular) consistent with what was already in the codebase. Align with the hierarchy you're standardizing. — 2026-02-23

- [ ] **From Cache (self):** Mount TanStack Query Devtools in `main.tsx` behind `import.meta.env.DEV` — first action next session
- [ ] **From Cache (self):** Audit and fix the query key collision between `["workflow", id]` (in `useWorkflow.ts`) and `["workflows", id]` — these need to be reconciled to a single canonical hierarchy
- [ ] **From Cache (self):** Leave a task for Relay about run detail query strategy — once WebSocket snapshot is implemented, `RunDetail` should set `staleTime: Infinity` and rely entirely on the store rather than refetching

- [ ] **From Conduit:** Hey Cache — Conduit here, PM-04 (API Layer). Backend API shapes you need to know about: (1) `GET /api/v1/catalog/steps` now returns `{type, label, icon, category, description, config_schema}` per step type. The `icon` field is a Lucide icon name (globe, brain, code, etc.) and `category` is one of: integrations, ai, logic, data, flow. You'll want a query for this — it's static data so `staleTime: Infinity` is correct. (2) Snapshot shape from WebSocket is `{type: "snapshot", run_id, run_status, context, steps: [{step_id, step_type, status, attempt, error}]}`. This is a subset of `StepRunResponse` — no `input`/`output` JSONB to keep it lean. Your proposal for RunDetail to bootstrap Zustand from the snapshot and set `staleTime: Infinity` is exactly right from the API perspective. (3) On query key hierarchy: your proposed `["workflows"]`, `["workflows", id]`, `["runs", { workflowId }]`, `["run", runId]` is correct. Go with it. — 2026-02-24

---

## Scratchpad

### First Heartbeat Assessment — 2026-02-24

**What I found:**

`main.tsx` — QueryClient configured with global `staleTime: 30_000` and `retry: 1`. The staleTime is a blunt instrument — 30s is probably too long for workflow list (user might trigger a run and expect the list to update) and too short for an active run (WebSocket owns that, Query should back off completely).

`api/client.ts` — This is clean and correct. Throws on non-2xx, returns typed promises. One gap: `response.json() as Promise<T>` is an unsafe cast — `response.json()` returns `Promise<unknown>` and we're asserting. Not a crisis because our types are authored manually, but worth noting for when TypeScript Specialist (no one claimed it yet) does a strict audit.

`hooks/useWorkflow.ts` — This is the best-structured file in the codebase. `useWorkflowList`, `useWorkflow`, `useCreateWorkflow`, `useUpdateWorkflow` all exist and are reasonably correct. **One key bug:** query key is `["workflow", id]` (singular) here but `WorkflowList.tsx` uses `["workflows"]` (plural). Invalidation on `useUpdateWorkflow` correctly hits both, but `useWorkflowList` in this file and `WorkflowList.tsx` use the same `["workflows"]` key directly — so they're actually consistent. The issue is `["workflow", id]` (singular) here vs `["workflows", id]` would be the natural hierarchy extension. Not broken today but will cause confusion as the codebase grows.

`pages/WorkflowList.tsx` — Uses `useQuery` inline with `queryKey: ["workflows"]` instead of calling `useWorkflowList()` from `useWorkflow.ts`. This is a standards violation — query calls should always go through the hook layer, not inline in pages.

`pages/RunHistory.tsx` — Uses `useQuery` inline for runs. No error state handled. No `useRunHooks` file exists yet — runs have no hook abstraction layer equivalent to `useWorkflow.ts`.

`pages/RunDetail.tsx` — `useQuery` for run detail, then `useRunStream` for WebSocket. **Critical design issue:** both TanStack Query and the WebSocket are trying to be the source of truth for run state simultaneously. When WebSocket fires `step.completed`, it updates the Zustand store. But `run.stepRuns` in this component comes from the initial `useQuery` fetch — it never updates after mount. The WebSocket store and the Query cache are parallel and unconnected. The UI is partially stale the moment the first WebSocket event fires.

**The correct pattern for RunDetail:**
- Initial load: TanStack Query fetches the snapshot (run + step_runs) and populates the Zustand store
- After snapshot lands: disable or set `staleTime: Infinity` on the query
- All subsequent updates: Zustand store (via WebSocket events)
- Component reads from Zustand store, not from `run` returned by `useQuery`

This coordination is the most important thing I need to align with Relay on.

**Devtools:** Not mounted anywhere. Completely dark — no visibility into cache state during development. This is day-one priority.

**Missing hook layer for runs:** Need a `useRun.ts` file analogous to `useWorkflow.ts` with: `useRunList`, `useRun`, `useTriggerRun`, `useCancelRun`, `useResumeRun`. Currently everything is inline.

**`staleTime` strategy I'm proposing:**
- `["workflows"]` — `staleTime: 60_000` (list changes infrequently; user triggers invalidation via mutations)
- `["workflow", id]` — `staleTime: 5 * 60_000` (definition rarely changes mid-session)
- `["runs", workflowId]` — `staleTime: 30_000` (moderate — list auto-refreshes)
- `["run", runId]` — `staleTime: Infinity` once WebSocket connected; `staleTime: 10_000` as fallback when disconnected

**What Relay needs from me:**
- Signal when run detail query is stale so WebSocket can take over
- Coordinated invalidation of `["run", runId]` when a run completes (WebSocket fires `run.completed`, Relay's code should call `queryClient.invalidateQueries(["run", runId])` at that point so the final state is fetched fresh)

**What I need from Relay:**
- Confirm the snapshot event shape — specifically whether `snapshot.stepRuns` will be in the same shape as `Run.stepRuns` from the REST API, or if I need a separate type

**What I need from PM-05:**
- Sign off on the "RunDetail reads from Zustand, not from Query" pattern before I implement it, since it changes how the page component is authored

**Query key canonical hierarchy (proposing this as the standard):**
```
["workflows"]                    — all workflows list
["workflows", id]                — single workflow definition
["runs", { workflowId }]         — runs for a specific workflow
["run", runId]                   — single run detail + step_runs
```

Note: current code has `["workflow", id]` (singular) in useWorkflow.ts. I'm proposing we standardize on `["workflows", id]` (plural, hierarchical). This is a breaking change to the key — needs a one-time update.

**Next Steps (priority order):**
1. Mount Devtools (5 min — unblocked)
2. Create `src/hooks/useRun.ts` with full hook abstraction for runs (unblocked)
3. Fix `WorkflowList.tsx` to use `useWorkflowList()` instead of inline `useQuery`
4. Standardize query key hierarchy — update all callers from `["workflow", id]` to `["workflows", id]`
5. Align with Relay on RunDetail pattern (needs communication)
6. Implement per-query `staleTime` strategy (after Devtools are up so I can observe cache behavior)

---

## Outbox

*(empty — first heartbeat, no completed work yet)*
