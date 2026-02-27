# Flow Matrx — Master Project Status & Direction

**Document Owner:** Project Management
**Last Updated:** 2026-02-27
**Status:** Active — Gap Analysis Complete

---

## Executive Summary

The project has strong foundational architecture but is currently **~35% complete toward a Phase 1 MVP**. The backend engine core is the most advanced area (~70% of Phase 1 scope), while the frontend is largely scaffolding (~20%), infrastructure has not been validated end-to-end (~40%), and the testing pipeline is effectively zero for integration scenarios.

**Critical finding:** Individual contributors have built good components in isolation, but the system has never run end-to-end. There is no proof that the pieces connect. The #1 priority is establishing a working vertical slice — from database to browser — and then building outward.

---

## Current State by Track

### PM-01: Database & Infrastructure (Axiom) — 40% Complete

| Deliverable | Status | Notes |
|-------------|--------|-------|
| D1: Supabase Project Setup | NOT STARTED | No live DB instance provisioned |
| D2: Migration 001 (Core Tables) | NOT STARTED | Matrx-ORM models exist in `db/models.py` (175 lines, all 4 tables), but no Alembic migrations written or run |
| D3: Migration 002 (Indexes) | NOT STARTED | No index migration |
| D4: Migration 003 (updated_at Trigger) | NOT STARTED | No trigger migration |
| D5: Matrx-ORM Model Generation | DONE | Models in `backend/db/models.py` match spec |
| D6: Docker Compose | PARTIAL | File updated to Postgres 18 + Redis 8, but never validated (`docker-compose up` not tested) |
| D7: Redis Setup | NOT STARTED | Redis in docker-compose but no app connectivity verified |
| D8: Supabase Auth Config | NOT STARTED | JWT middleware exists in code but no secret configured |
| D9: Seed Data Script | PARTIAL | `scripts/seed-workflow.py` exists with 1 sample workflow, spec requires 3 |
| D10: .env.example | DONE | Complete with all required variables |
| D11: Production Dockerfile | NOT STARTED | No Dockerfiles for production |

**Blockers produced:** Every other track is blocked by PM-01 not having a running database with schema applied.

**Self-reported blockers from Axiom (2026-02-23):**
- DB instance not provisioned
- Migrations not run
- Seed data incomplete (1 of 3 workflows)

### PM-02: Execution Engine (Forge) — 70% Complete

| Deliverable | Status | Notes |
|-------------|--------|-------|
| D1: Engine Exceptions | DONE | `EngineError`, `PauseExecution`, `StepTimeout` — 26 lines |
| D2: Event Bus | DONE | Persist + broadcast, queue-based subscribers — 77 lines |
| D3: Event Types | DONE | All 13 types as StrEnum — 22 lines |
| D4: Graph Helper | DONE | Ready steps, branch nodes, upstream IDs — 80 lines |
| D5: Template Resolution | DONE | Type preservation, deep_get, Jinja2 fallback — 61 lines |
| D6: Safe Expression Eval | DONE | AST whitelist, builtins blocked — 36 lines |
| D7: Workflow Validation | DONE | All 7 error categories — 97 lines |
| D8: Execution Engine | DONE | Full loop with retry, conditions, parallel — 379 lines |
| D9: Background Task (ARQ) | NOT STARTED | ARQ imported but not wired; using BackgroundTasks |

**Tests written:** 59 passing (graph: 12, templates: 19, safe_eval: 13, validation: 15)
**Critical gaps:**
- Approval data does NOT flow into `runs.context` — downstream `{{approval_step.field}}` templates will fail
- No monotonic event sequence numbers — WebSocket reconnection can't detect missed events
- No integration tests against a real (or mocked) database — all tests are pure unit tests
- ARQ not wired — engine runs in-process only

### PM-03: Step Handlers (Vertex) — 55% Complete

| Deliverable | Status | Notes |
|-------------|--------|-------|
| D1: StepHandler Base Class | DONE | `execute()` + `validate_output()` — 46 lines |
| D2: HTTP Request | DONE | httpx with timeout, raise_for_status — 48 lines |
| D3: LLM Call | PLACEHOLDER | Uses direct httpx to OpenAI; marked for replacement with AI Matrx packages |
| D4: Inline Code | DONE | Sandboxed exec with safe builtins — 100 lines |
| D5: Condition | DONE | Schema only, engine handles logic — 25 lines |
| D6: Database Query | PARTIAL | Expects `__db_conn__` in context but executor never injects it |
| D7: Transform | DONE | Pass-through of resolved templates — 25 lines |
| D8: Delay | DONE | asyncio.sleep — 25 lines |
| D9: Wait for Approval | DONE | Engine handles pause/resume — 24 lines |
| D10: Wait for Event | STUB | Returns dict, no real subscription mechanism |
| D11: Send Email | STUB | Returns `queued` status, no SMTP integration |
| D12: Webhook | DONE | POST with optional HMAC — 35 lines |
| D13: For Each | STUB | Returns items but doesn't iterate sub-steps |
| D14: Step Registry | DONE | All types mapped — 43 lines |
| D15: Step Catalog | PARTIAL | Duplicate: exists in both `catalog.py` AND `registry.py` |

**Tests written:** 11 (8 passing, 3 failing due to mock setup issues with AsyncMock)
**Critical gaps:**
- LLM handler is acknowledged placeholder
- Database query handler wiring broken (no connection in context)
- Duplicate catalog code needs consolidation
- 3 test failures unresolved
- for_each, wait_for_event, send_email are non-functional stubs

### PM-04: API Layer & WebSocket (Conduit) — 65% Complete

| Deliverable | Status | Notes |
|-------------|--------|-------|
| D1: Pydantic Schemas | DONE | All request/response models — 108 lines |
| D2: FastAPI App Setup | DONE | Lifespan, CORS, health check — 40 lines |
| D3: Dependency Injection | PARTIAL | `get_current_user` exists but NOT wired into any route |
| D4: Main Router | DONE | All sub-routers included — 15 lines |
| D5: Workflow Endpoints | DONE | All 8 endpoints including publish/validate/duplicate — 114 lines |
| D6: Run Endpoints | DONE | All endpoints including steps/events/cancel/resume/retry — 140 lines |
| D7: Trigger Endpoints | DONE | Manual + webhook triggers — 90 lines |
| D8: Catalog Endpoint | DONE | Returns step metadata — 28 lines |
| D9: WebSocket Endpoint | DONE | Snapshot on connect + live streaming — 66 lines |
| D10: Auth Middleware | NOT WIRED | Code exists but no route uses `Depends(get_current_user)` |
| D11: CORS Config | DONE | In main.py |
| D12: DB Query Functions | PARTIAL | workflows.py has CRUD, runs.py minimal, step_runs.py minimal |

**Critical gaps:**
- Zero authentication on any endpoint
- No pagination on list endpoints (returns all rows unbounded)
- No structured error response middleware
- BackgroundTasks used instead of ARQ (acceptable for Phase 1)
- DB query layer is thin — missing create_run, update_run, get_step_ids_by_status
- The API client URL paths in frontend don't match the actual backend routes

### PM-05: Frontend (UNASSIGNED) — 20% Complete

| Deliverable | Status | Notes |
|-------------|--------|-------|
| D1: Project Scaffold | DONE | Vite 7.3 + React 19 + TS 5.9 + Tailwind 4.2 + Biome |
| D2: CSS Entry Point | DONE | index.css with `@import "tailwindcss"` |
| D3: shadcn/ui Components | **NOT DONE** | `components.json` configured but `src/components/ui/` is EMPTY — zero components installed |
| D4: Router Setup | DONE | 4 routes in App.tsx |
| D5: API Client | PARTIAL | Base client exists; URL paths don't match backend |
| D6: API Hooks (TanStack Query) | PARTIAL | Raw API functions exist, but NO `useQuery`/`useMutation` hooks except in WorkflowBuilder |
| D7: Zustand Stores | DONE | workflowStore (33 lines) + runStore (100 lines) both properly typed |
| D8: WebSocket Hook | DONE | useRunStream (113 lines) — full implementation with reconnection |
| D9: BaseNode | MINIMAL | 26 lines, no status-driven styling per spec |
| D10: Node Components | **STUBS** | All 7 are 6-line wrappers that just pass a color to BaseNode — no icons, no preview content |
| D11: Config Panels | PARTIAL | 6 exist (24-44 lines each), but use raw HTML `<select>`/`<input>` instead of shadcn/ui, and none use React Hook Form + Zod |
| D12: NodeConfigPanel | DONE | Container that routes to correct panel — 29 lines |
| D13: Step Palette | PARTIAL | Hardcoded step list instead of fetching from catalog API — 43 lines |
| D14: WorkflowBuilder Page | MINIMAL | Basic layout but missing: save, publish, run controls in toolbar |
| D15: Run Controls | PARTIAL | Buttons exist but limited functionality — 46 lines |
| D16: Run Overlay | PARTIAL | Basic overlay — 27 lines |
| D17: Step Output | PARTIAL | Basic JSON display — 33 lines |
| D18: TemplateInput | PARTIAL | Basic input, no autocomplete for `{{context.*}}` — 42 lines |
| D19: WorkflowList Page | MINIMAL | Lists workflows, missing: create, filter, delete actions |
| D20: RunHistory Page | MINIMAL | Basic list — 37 lines |
| D21: RunDetail Page | PARTIAL | Shows events and metadata — 71 lines |
| D22: Shared Components | PARTIAL | CodeEditor, StatusBadge, EdgeLabel exist |
| D23: Auto-Layout | DONE | dagre-based hook — 35 lines |
| D24: Client-Side Validation | PARTIAL | Basic checks — 27 lines |

**Missing node types:** TransformNode, SendEmailNode, WebhookNode, WaitForEventNode, ForEachNode
**Missing config panels:** DelayConfig, TransformConfig, SendEmailConfig, WebhookConfig, WaitForEventConfig, ForEachConfig

**Critical Frontend Gaps:**
1. **ZERO shadcn/ui components installed** — every form uses raw HTML elements, violating Non-Negotiable #15
2. **React Hook Form + Zod not used anywhere** — installed but 0 usage
3. **date-fns not used** — timestamps shown as raw strings
4. **Sonner `<Toaster>` not mounted** — no toast notifications
5. **TanStack DevTools not mounted** — installed but invisible
6. **No test files** — 0% coverage vs 70% target
7. **Node components are stubs** — no icons (Lucide), no preview content, no status-driven styling
8. **API URL paths mismatched** — frontend calls `/runs/workflow/{id}/trigger` but backend is `/api/v1/workflows/{id}/run`
9. **PM-05 is unassigned** — no one owns the frontend track

---

## Makefile Issues

The Makefile uses wrong package managers in 6 targets:
- `backend-install` uses `pip` → should use `uv sync`
- `frontend-install` uses `npm` → should use `pnpm install`
- `test-frontend` uses `npm run test` → should use `pnpm test`
- `lint-backend` uses `ruff` → should use the project's Python linting
- `lint-frontend` uses `npm run lint` → should use `pnpm biome check --write src`
- `seed` uses `python` → should use `uv run python`

---

## Cross-Team Integration Gaps

### 1. Frontend ↔ Backend API Contract Mismatch
The frontend API client (`src/api/runs.ts`, `src/api/workflows.ts`) does not match the actual backend routes:
- Frontend: `POST /runs/workflow/{id}/trigger` → Backend: `POST /api/v1/workflows/{id}/run`
- Frontend: `GET /runs/workflow/{id}` → Backend: `GET /api/v1/runs?workflow_id={id}`
- Frontend uses `WorkflowDefinition` from shared types, backend returns `WorkflowResponse` with different field names

### 2. Shared Types ↔ Backend Schemas Drift
- `packages/shared/types/run.ts` has `StepRunStatus = "waiting_approval"` but backend uses `"waiting"`
- Frontend `Run.triggerPayload` vs Backend `Run.input`
- `WorkflowNode.config` in shared types vs `node.data.config` in backend

### 3. Event Format ↔ Frontend Handler
- Shared types define `SnapshotEvent` with specific shape, but backend `ws.py` sends a different snapshot structure
- `useRunStream.ts` expects `msg.type === "snapshot"` with `msg.step_statuses` — backend sends `msg.steps` array

### 4. No End-to-End Path
No one has ever:
- Started Docker Compose → applied migrations → seeded data → started backend → started frontend → created a workflow → run it → watched WebSocket events update the UI

---

## Priority Action Items (Next Sprint)

### P0 — Unblock Everything (PM-01 / Axiom)
1. Get Postgres running (Docker Compose or Supabase)
2. Apply schema migrations (write Alembic migrations OR use Matrx-ORM migration tools)
3. Verify all 4 tables + indexes + trigger exist
4. Complete seed data script (3 workflows per spec)
5. Verify `docker-compose up` brings up all services with health checks

### P1 — Prove the System Works (All Tracks)
6. Fix API client URL paths in frontend to match backend routes
7. Fix shared type mismatches (waiting_approval → waiting, triggerPayload → input)
8. Fix snapshot format mismatch between backend ws.py and frontend useRunStream
9. Run a manual end-to-end test: create workflow → run → verify WebSocket events
10. Write the first chained integration test (see Testing Strategy below)

### P2 — Frontend Catch-Up (PM-05 / Unassigned)
11. Install shadcn/ui components (`pnpm dlx shadcn@latest add button badge card input select dialog textarea label separator switch tabs scroll-area`)
12. Rebuild all config panels using React Hook Form + Zod + shadcn/ui
13. Rebuild BaseNode with status-driven styling per spec
14. Rebuild all node components with Lucide icons and preview content
15. Wire missing node types and config panels (Transform, SendEmail, Webhook, WaitForEvent, ForEach)

### P3 — Backend Polish (PM-02, PM-03, PM-04)
16. Wire approval data into context in resume endpoint
17. Add pagination to list endpoints
18. Fix database_query handler (inject connection via engine, not context)
19. Consolidate duplicate catalog code (catalog.py vs registry.py STEP_CATALOG)
20. Fix 3 failing step handler tests (AsyncMock → MagicMock for sync httpx methods)

### P4 — Testing Infrastructure
21. Create chained integration test suite (see below)
22. Add API endpoint tests using httpx.AsyncClient
23. Add frontend component tests using Vitest + React Testing Library
24. Set up CI pipeline (run tests on PR)

---

## Chained Integration Test Strategy

### Philosophy

> "When I asked developers to create their own unit tests, I find that they often create tests that are adjusted to ensure results as opposed to those that truly test if the data naturally flowing into the system can generate the data that naturally needs to flow out to make the next step work."

The answer: **contract-driven chained tests** where the output of one test becomes the input of the next, mimicking real data flow.

### The Chain

```
Test 1: Schema Validation
    OUTPUT → verified table structure
        ↓
Test 2: Seed Data Insert
    INPUT  ← verified table structure
    OUTPUT → workflow_id of inserted workflow
        ↓
Test 3: Workflow Retrieval
    INPUT  ← workflow_id
    OUTPUT → workflow definition (nodes + edges)
        ↓
Test 4: Workflow Validation
    INPUT  ← workflow definition
    OUTPUT → validation result (valid: true)
        ↓
Test 5: Run Creation
    INPUT  ← workflow_id + run input
    OUTPUT → run_id
        ↓
Test 6: Engine Execution
    INPUT  ← run_id
    OUTPUT → completed run with context populated
        ↓
Test 7: Event Verification
    INPUT  ← run_id
    OUTPUT → ordered list of events with correct types + payloads
        ↓
Test 8: WebSocket Snapshot
    INPUT  ← run_id (after completion)
    OUTPUT → snapshot with all step statuses = completed
        ↓
Test 9: Context Accumulation
    INPUT  ← completed run context
    OUTPUT → verify each step's output is accessible via {{step_id.field}} templates
        ↓
Test 10: Frontend Rendering
    INPUT  ← snapshot data
    OUTPUT → verify each node renders correct status styling
```

### Implementation Pattern

```python
# tests/integration/test_full_pipeline.py

import pytest

# Shared state flows between tests via module-level fixture
@pytest.fixture(scope="module")
def pipeline_state():
    """Accumulates outputs across the test chain."""
    return {}

class TestFullPipeline:
    """Tests run in order. Each builds on the previous."""

    async def test_01_schema_exists(self, db_pool, pipeline_state):
        """Verify all 4 tables exist with correct columns."""
        tables = await db_pool.fetch(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )
        table_names = {t["table_name"] for t in tables}
        assert {"workflows", "runs", "step_runs", "run_events"} <= table_names
        pipeline_state["schema_verified"] = True

    async def test_02_seed_workflow(self, db_pool, pipeline_state):
        """Insert a real workflow and verify it persists."""
        assert pipeline_state.get("schema_verified"), "Schema must exist first"
        workflow = await create_test_workflow(db_pool)
        pipeline_state["workflow_id"] = str(workflow["id"])
        pipeline_state["workflow_definition"] = workflow["definition"]

    async def test_03_validate_workflow(self, pipeline_state):
        """Validate the seeded workflow definition."""
        definition = pipeline_state["workflow_definition"]
        errors = validate_workflow(definition)
        assert errors == [], f"Workflow invalid: {errors}"
        pipeline_state["validation_passed"] = True

    async def test_04_create_run(self, pipeline_state):
        """Create a run against the workflow."""
        run = await create_run(pipeline_state["workflow_id"], input={"user_id": "123"})
        assert run["status"] == "pending"
        pipeline_state["run_id"] = str(run["id"])
        pipeline_state["run_input"] = run["input"]

    async def test_05_execute_run(self, engine, pipeline_state):
        """Execute the run and verify completion."""
        await engine.execute_run(pipeline_state["run_id"])
        run = await get_run(pipeline_state["run_id"])
        assert run["status"] == "completed"
        pipeline_state["run_context"] = run["context"]

    async def test_06_verify_events(self, db_pool, pipeline_state):
        """Verify events were emitted in correct order with correct payloads."""
        events = await get_run_events(pipeline_state["run_id"])
        event_types = [e["event_type"] for e in events]
        assert event_types[0] == "run.started"
        assert event_types[-1] == "run.completed"
        # Every step must have started + completed
        step_events = [e for e in events if e["step_id"] is not None]
        for step_id in get_step_ids(pipeline_state["workflow_definition"]):
            step_specific = [e for e in step_events if e["step_id"] == step_id]
            types = [e["event_type"] for e in step_specific]
            assert "step.started" in types
            assert "step.completed" in types or "step.skipped" in types
        pipeline_state["events_verified"] = True

    async def test_07_context_accumulation(self, pipeline_state):
        """Verify each step's output is in context under its step_id."""
        context = pipeline_state["run_context"]
        assert "input" in context
        definition = pipeline_state["workflow_definition"]
        for node in definition["nodes"]:
            if node["type"] not in ("condition", "wait_for_approval"):
                assert node["id"] in context, f"Missing context for step {node['id']}"

    async def test_08_template_resolution(self, pipeline_state):
        """Verify downstream steps can resolve upstream references."""
        context = pipeline_state["run_context"]
        # If step_2 references {{step_1.body}}, verify that resolves
        from app.engine.templates import resolve_templates
        template = "{{step_1.body}}"  # Example
        result = resolve_templates(template, context)
        assert result is not None

    async def test_09_websocket_snapshot(self, pipeline_state):
        """Verify WebSocket snapshot contains correct final state."""
        step_runs = await get_step_runs(pipeline_state["run_id"])
        for sr in step_runs:
            assert sr["status"] in ("completed", "skipped")

    async def test_10_step_run_records(self, pipeline_state):
        """Verify step_run records have resolved input (not templates)."""
        step_runs = await get_step_runs(pipeline_state["run_id"])
        for sr in step_runs:
            input_str = str(sr["input"])
            assert "{{" not in input_str, f"Unresolved template in step_run input: {input_str}"
```

### Frontend Test Chain

```typescript
// frontend/src/tests/integration/pipeline.test.tsx
// Mirrors the backend chain but tests UI rendering

describe("Frontend Pipeline", () => {
  const state: Record<string, unknown> = {};

  test("01: Zustand store accepts snapshot data", () => {
    const snapshot = createMockSnapshot(); // matches backend format
    useRunStore.getState().setSnapshot(snapshot.steps);
    const statuses = useRunStore.getState().stepStatuses;
    expect(Object.keys(statuses).length).toBeGreaterThan(0);
    state.snapshot = snapshot;
  });

  test("02: BaseNode renders correct styling per status", () => {
    // For each status type, render BaseNode and verify CSS classes
    for (const status of ["pending", "running", "completed", "failed", "skipped", "waiting"]) {
      const { container } = render(<BaseNode status={status} />);
      // Verify status-specific border/bg classes are applied
    }
  });

  test("03: Live event updates store correctly", () => {
    const event = { event_type: "step.completed", step_id: "step_1", payload: { status: "completed" } };
    useRunStore.getState().setStepStatus(event.step_id, event.payload);
    expect(useRunStore.getState().stepStatuses["step_1"].status).toBe("completed");
  });
});
```

### Key Properties of This Test Design

1. **Tests fail forward** — if test_02 fails, test_03+ skip with a clear "prerequisite not met" message
2. **Real data flows** — no mocks for data shape; actual workflow definitions, actual context dicts
3. **Contract enforcement** — test_06 (events) proves the backend emits what test_03 (frontend) expects
4. **No "adjusted" tests** — we don't create artificial data that happens to pass; we use the same workflow definition the seed script uses
5. **Cross-boundary** — backend test_07 (context) feeds into frontend test_01 (snapshot rendering)

---

## Team Roster Status

| Codename | Role | Active? | Last Seen |
|----------|------|---------|-----------|
| Arman | Project Owner | Yes | 2026-02-23 |
| Axiom | PM-01: Database & Infrastructure | Yes | 2026-02-23 |
| Forge | PM-02: Execution Engine | Yes | 2026-02-24 |
| Vertex | PM-03: Step Handlers | Yes | 2026-02-24 |
| Conduit | PM-04: API Layer & WebSocket | Yes | 2026-02-24 |
| Relay | Realtime Integration (Team 4) | Yes | 2026-02-23 |
| Cache | TanStack Query (Team 2) | Yes | 2026-02-23 |
| Pulse | FastAPI/ASGI (Team 1) | Yes | 2026-02-23 |
| **???** | **PM-05: Frontend** | **UNASSIGNED** | — |

**Critical:** PM-05 (Frontend) has no owner. This is the most user-facing track and it's 80% incomplete. This must be assigned immediately.

---

## Decision Log

| Date | Decision | Rationale | Made By |
|------|----------|-----------|---------|
| 2026-02-24 | BackgroundTasks for Phase 1 (not ARQ) | Zero-config, adequate for dev | Conduit |
| 2026-02-24 | Inline condition eval (not handler) | Conditions are engine logic, not business logic | Forge/Axiom |
| 2026-02-24 | StrictUndefined for templates | Missing keys are bugs, not silent fallbacks | Forge |

---

## How to Use This Document

1. **Arman** reviews this weekly and adjusts priorities
2. **PMs** check their track section before each shift
3. **Action items** flow from here → into individual PM inboxes
4. **Status updates** flow from PM outboxes → back into this document
5. **Flags and blockers** are surfaced here for visibility

This is the single place where the project's overall health is visible.
