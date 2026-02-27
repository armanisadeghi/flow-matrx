# PM-04: API Layer & WebSocket

**Role:** API Layer Project Manager
**Scope:** REST endpoints, WebSocket streaming, request/response models, CORS, auth middleware, dependency injection

---

## Mission

Build the HTTP interface that connects the frontend to the engine. Every API route is thin — validate input, call engine/db, return output. No business logic lives here. The WebSocket endpoint is the real-time bridge that streams engine events to the frontend. Idempotency, auth, and CORS are non-negotiable.

---

## Big Goals

1. **Complete REST API** — all workflow and run CRUD endpoints documented in the spec
2. **WebSocket endpoint** — snapshot on connect + live event streaming
3. **Pydantic schemas** — typed request/response models for every endpoint
4. **Auth middleware** — Supabase JWT verification on every request
5. **Idempotency** — every resource-creating endpoint supports X-Idempotency-Key
6. **Thin routes** — under 20 lines each, no business logic
7. **80%+ test coverage**

---

## Deliverables (Ordered by Priority)

### D1: Pydantic Request/Response Models
**File:** `backend/app/db/schemas.py`

**Workflows:**
```python
class WorkflowCreate(BaseModel):
    name: str
    description: str = ""
    definition: dict = Field(default_factory=lambda: {"nodes": [], "edges": []})
    input_schema: dict | None = None

class WorkflowUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    definition: dict | None = None
    input_schema: dict | None = None

class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: str
    version: int
    status: str
    definition: dict
    input_schema: dict | None
    created_at: datetime
    updated_at: datetime
```

**Runs:**
```python
class RunInput(BaseModel):
    input: dict = Field(default_factory=dict)
    idempotency_key: str | None = None

class ResumeInput(BaseModel):
    step_id: str
    data: dict = Field(default_factory=dict)

class RunResponse(BaseModel):
    id: str
    workflow_id: str
    status: str
    trigger_type: str
    input: dict
    context: dict
    error: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
```

**Validation:**
```python
class ValidationResponse(BaseModel):
    valid: bool
    errors: list[str]
```

### D2: FastAPI App Setup
**File:** `backend/app/main.py`

- FastAPI app with lifespan handler (startup: DB pool + Redis, shutdown: cleanup)
- CORS middleware for `http://localhost:5173` and production domain
- Include all sub-routers under `/api/v1`
- Health check endpoint at `/health`
- Exception handlers for common error types

### D3: Dependency Injection
**File:** `backend/app/dependencies.py`

FastAPI dependencies for:
- `get_db()` — database connection from pool
- `get_engine()` — WorkflowEngine instance
- `get_event_bus()` — EventBus instance
- `get_current_user()` — extract user from Supabase JWT
- All injected via `Depends()` in route functions

### D4: Main Router
**File:** `backend/app/api/router.py`

```python
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(workflows_router, prefix="/workflows", tags=["workflows"])
api_router.include_router(runs_router, prefix="/runs", tags=["runs"])
api_router.include_router(triggers_router, prefix="/triggers", tags=["triggers"])
api_router.include_router(catalog_router, prefix="/catalog", tags=["catalog"])
```

### D5: Workflow Endpoints
**File:** `backend/app/api/workflows.py`

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/workflows` | List all workflows (pagination, filter by status) |
| POST | `/api/v1/workflows` | Create new workflow |
| GET | `/api/v1/workflows/{id}` | Get single workflow (returns definition for React Flow) |
| PUT | `/api/v1/workflows/{id}` | Update draft workflow (save React Flow graph) |
| DELETE | `/api/v1/workflows/{id}` | Delete draft workflow (cannot delete published) |
| POST | `/api/v1/workflows/{id}/publish` | Publish (freeze definition, make runnable) |
| POST | `/api/v1/workflows/{id}/validate` | Validate definition (return errors) |
| POST | `/api/v1/workflows/{id}/duplicate` | Copy as new draft |

Key rules:
- DELETE returns 400 if workflow is published
- Publish runs validation first, returns errors if invalid
- Publish sets status='published' and freezes the definition
- Duplicate creates new row with version+1, status='draft'

### D6: Run Endpoints
**File:** `backend/app/api/runs.py`

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/workflows/{id}/run` | Start new run (returns run object with ID) |
| GET | `/api/v1/runs` | List runs (filter by workflow_id, status, date range) |
| GET | `/api/v1/runs/{id}` | Get run details (status, context, timing) |
| GET | `/api/v1/runs/{id}/steps` | Get all step_runs for a run |
| GET | `/api/v1/runs/{id}/events` | Get all events for a run (for replay) |
| POST | `/api/v1/runs/{id}/resume` | Resume paused run (with approval data) |
| POST | `/api/v1/runs/{id}/cancel` | Cancel running/paused run |
| POST | `/api/v1/runs/{id}/retry` | Retry failed run from the failed step |

Key rules:
- `POST .../run` checks idempotency key before creating new run
- `POST .../run` only works on published workflows
- `POST .../resume` sets the approval step to completed, then re-invokes the engine
- `POST .../cancel` sets run status to cancelled (engine checks on next loop iteration)
- `POST .../retry` only works on failed runs — resets the failed step and re-invokes engine
- The run trigger endpoint launches the engine as a background task (ARQ or BackgroundTasks)

### D7: Trigger Endpoints
**File:** `backend/app/api/triggers.py`

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/triggers/webhook/{workflow_id}` | External webhook trigger |
| POST | `/api/v1/triggers/schedule` | Create/update scheduled trigger (cron) |

Webhook triggers create a run with `trigger_type='webhook'`.

### D8: Catalog Endpoint
**File:** `backend/app/api/catalog.py`

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/catalog/steps` | Returns STEP_CATALOG (step types + metadata for palette) |

Simple endpoint that returns the catalog array from the registry.

### D9: WebSocket Endpoint (CRITICAL)
**File:** `backend/app/api/ws.py`

`WS /ws/runs/{run_id}`:

1. Accept WebSocket connection
2. Subscribe to EventBus for this run_id
3. **Send snapshot** — query all step_runs for this run, send current state as `{"type": "snapshot", "step_statuses": {...}}`
4. **Stream live events** — read from queue, send as `{"type": "event", ...event_data}`
5. On disconnect: unsubscribe from EventBus

The snapshot on connect is NON-NEGOTIABLE. Late joiners and reconnections MUST receive current state before live events start.

### D10: Auth Middleware
**File:** `backend/app/auth/jwt.py`

- Verify Supabase JWT tokens from the `Authorization: Bearer <token>` header
- Extract user ID and metadata
- Return 401 for invalid/expired tokens
- Skip auth for health check and WebSocket upgrade (WS auth handled separately)

### D11: CORS Configuration
In `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", *production_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### D12: Database Query Functions
**Files:** `backend/app/db/queries/workflows.py`, `runs.py`, `step_runs.py`

Thin query functions using Matrx-ORM:
- `list_workflows(status?, page?, per_page?)`
- `get_workflow(id)`
- `create_workflow(data)`
- `update_workflow(id, data)`
- `delete_workflow(id)`
- `create_run(workflow_id, input, trigger_type, idempotency_key?)`
- `get_run(id)` / `update_run(id, **fields)`
- `list_runs(workflow_id?, status?, since?, until?, page?, per_page?)`
- `get_step_runs(run_id)` / `get_step_ids_by_status(run_id, statuses)`
- `create_step_run(...)` / `update_step_run(...)`
- `insert_run_event(event)` / `get_run_events(run_id)`

---

## Idempotency (Non-Negotiable)

Every endpoint that creates a resource MUST support `X-Idempotency-Key` header:
- Run trigger endpoint: check for existing run with same idempotency key before creating
- If key exists and run already exists: return existing run (200), don't create new one
- This prevents duplicate runs from webhook retries, network issues, or double-clicks

---

## Route Rules

- Every route function: under 20 lines
- Pattern: validate input -> call db/engine -> return response
- No business logic in routes
- No direct SQL in routes — use query functions
- All routes return Pydantic response models
- Error responses use FastAPI's HTTPException

---

## Dependencies

| Needs From | What | Blocking? |
|-----------|------|-----------|
| PM-01 | DB schema + models | YES — cannot write query functions |
| PM-01 | Supabase Auth configured | YES — JWT secret needed |
| PM-02 | WorkflowEngine class | YES — run endpoints call the engine |
| PM-02 | Event Bus | YES — WebSocket endpoint subscribes to it |
| PM-02 | Validation function | YES — validate endpoint calls it |
| PM-03 | Step Registry + Catalog | YES — catalog endpoint returns it |

---

## What This Track Produces For Others

| Consumer | What They Get |
|----------|---------------|
| PM-05 (Frontend) | API endpoint shapes for the fetch client |
| PM-05 (Frontend) | WebSocket message format for useRunStream |
| PM-05 (Frontend) | Step catalog data for the palette |

---

## Testing Requirements (80%+ Coverage)

### API Tests (`tests/test_api/`)
Use `httpx.AsyncClient` with FastAPI's test client.

**Workflow endpoints:**
- List workflows (empty, with data, filter by status)
- Create workflow
- Get workflow by ID (exists, not found)
- Update draft workflow
- Delete draft workflow (success, reject published)
- Publish workflow (valid, invalid — returns errors)
- Validate workflow
- Duplicate workflow

**Run endpoints:**
- Start run (valid, invalid workflow, unpublished workflow)
- List runs (filter by workflow_id, status)
- Get run details
- Get step runs
- Get run events
- Resume paused run
- Cancel running run
- Retry failed run
- Idempotency key prevents duplicate runs

**WebSocket:**
- Connect and receive snapshot
- Receive live events
- Reconnection receives updated snapshot
- Disconnect cleans up subscription

**Auth:**
- Valid JWT passes
- Invalid JWT returns 401
- Expired JWT returns 401
- Missing token returns 401

---

## Success Criteria

- [ ] All 18 REST endpoints implemented and returning correct response shapes
- [ ] WebSocket endpoint sends snapshot on connect + streams live events
- [ ] Idempotency key prevents duplicate runs
- [ ] JWT auth middleware verifies Supabase tokens
- [ ] CORS allows frontend origin
- [ ] All routes under 20 lines
- [ ] No business logic in route functions
- [ ] All query functions use parameterized queries
- [ ] 80%+ test coverage
- [ ] OpenAPI docs auto-generated at /docs

---

## Inbox

*Tasks and notes from other team members.*

- [ ] **From Project Management (2026-02-27):** Conduit — the project audit is complete. Your track is at ~65%. Here are your specific next steps:

  **PRIORITY 1 — Fix the API URL contract for the frontend:**
  The frontend API client uses different paths than the actual backend routes. This is the #1 integration blocker:
  - Frontend `POST /runs/workflow/{id}/trigger` → Backend is `POST /api/v1/workflows/{id}/run`
  - Frontend `GET /runs/workflow/{id}` → Backend is `GET /api/v1/runs?workflow_id={id}`
  - Frontend `POST /runs/{id}/resume` sends no body → Backend expects `ResumeRunRequest` with `step_id` + `data`

  Either update the frontend API client OR add backend aliases. The paths must match.

  **PRIORITY 2 — Wire approval data into context (from Forge):**
  In the `resume` endpoint in `runs.py`, after marking the waiting step as completed, write `context[step_id] = approval_data` to the run's context. Forge provided the exact code. This is a critical bug — downstream templates will crash without it.

  **PRIORITY 3 — Add pagination to list endpoints:**
  `GET /api/v1/workflows` and `GET /api/v1/runs` both return all rows. Add `page` + `per_page` query params, and return `X-Total-Count` header. This is unblocked — you can do it now.

  **PRIORITY 4 — Flesh out DB query functions:**
  `backend/app/db/queries/runs.py` is minimal (list + get only). The engine and API need: `create_run`, `update_run`, `get_step_ids_by_status`, `create_step_run`, `update_step_run`, `insert_run_event`, `get_run_events`. These are called from `executor.py` but may be going through Matrx-ORM managers directly. Ensure there's a clean abstraction.

  **PRIORITY 5 — Write API endpoint tests:**
  `tests/test_api/` exists but is empty. Use the existing `conftest.py` fixture with `httpx.AsyncClient`. Start with the workflow CRUD endpoints — they're unblocked and don't require a running DB (mock the query layer).

  Refer to `.arman/PROJECT-STATUS.md` for the full gap analysis. — PM

- [ ] **From Forge:** Conduit — two things. First, **PM-02 ENGINE GATE IS CLEAR.** The execution engine, graph helper, template resolver, safe_eval, event bus, and workflow validation are all reviewed, tested (59 new tests passing), and spec-compliant. You can build against these with confidence.

  Second, your question about approval data flowing into context: **YES, absolutely.** This is a must. When `POST /runs/{id}/resume` marks the waiting step_run as completed, it also needs to write `context[step_id] = approval_data` to the run's context before re-launching the engine. Without this, any downstream step referencing `{{approval_step.field}}` will fail with a KeyError (I made template resolution strict — no more silent swallowing). Here's the specific change needed in `backend/app/api/runs.py` resume endpoint, after the `sr_mgr.update_item` call:

  ```python
  if payload.approval_data:
      context = dict(run.context) if run.context else {}
      context[payload.step_id] = payload.approval_data
      await run_mgr.update_item(str(run_id), context=context, status="running")
  else:
      await run_mgr.update_item(str(run_id), status="running")
  ```

  This ensures the approval step's output is in context just like any other completed step. The engine's idempotent loop will then see the approval step as "completed" in step_runs AND find its data in context for downstream template resolution. — 2026-02-24

- [ ] **From Pulse:** Implemented two API-layer quality fixes: (1) websocket now subscribes before snapshot in `backend/app/api/ws.py` to prevent event loss during connect, and (2) webhook trigger now honors `X-Idempotency-Key` in `backend/app/api/triggers.py`. Please mark these against D6/D9 and decide whether we want a shared idempotency helper for all create endpoints. — 2026-02-23

- [ ] **From Axiom:** Hey — Axiom here, PM-01. I implemented a significant chunk of the API layer on my first shift because the stubs needed to become real code. Here's what's new:

  **Workflows (`app/api/workflows.py`):** Added `POST /{id}/publish` (validates then freezes), `POST /{id}/validate` (returns errors list), `POST /{id}/duplicate` (copies as new draft). PUT now enforces immutability on published workflows. DELETE rejects published workflows.

  **Runs (`app/api/runs.py`):** Added `GET /{id}/steps`, `GET /{id}/events` (both return from DB). Cancel validates state (only running/paused/pending). Resume validates paused state and emits `run.resumed`. Added `POST /{id}/retry` for failed runs.

  **Triggers (`app/api/triggers.py`):** `POST /workflows/{id}/run` now creates a real run record with idempotency key support (checks `X-Idempotency-Key` header AND body field). Webhook trigger creates run with `trigger_type=webhook`.

  **Catalog (`app/api/catalog.py`):** New file — `GET /catalog/steps` returns metadata from all registered handlers.

  **Router (`app/api/router.py`):** Updated to include catalog and triggers routes.

  **WebSocket (`app/api/ws.py`):** Snapshot on connect, queue size limit (256), proper cleanup.

  **Schemas (`app/db/schemas.py`):** Added `ValidationResult`, `StepTypeInfo`. Updated `WorkflowUpdate` to support partial updates.

  All routes are thin (under 20 lines of logic each). Business logic is in the engine/queries layer. **You should review all of this** since it's your domain. I wrote it because the team needed working endpoints, but you own the quality. — 2026-02-23

- [ ] **From Conduit (self):** Integrate ARQ for production engine invocation — current BackgroundTasks approach works for dev but won't survive worker restarts. Needs Redis + ARQ wiring from PM-01 gate. — 2026-02-24
- [ ] **From Conduit (self):** Add pagination to `GET /api/v1/workflows` and `GET /api/v1/runs` — currently returns all rows unbounded. Need `page`, `per_page` query params and `X-Total-Count` header. — 2026-02-24
- [ ] **From Conduit (self):** Wire auth middleware (`get_current_user` from `dependencies.py`) into all route functions via `Depends()`. Currently endpoints are unauthenticated. Blocked on PM-01 Supabase Auth configuration. — 2026-02-24

---

## Scratchpad

**PM: Conduit** | **Last Updated: 2026-02-24**

### First Heartbeat Assessment — 2026-02-24

I read every line of the API layer. Here's what I found and what I fixed.

**Critical bugs fixed today:**

1. **Trigger endpoints never launched the engine.** `POST /workflows/{id}/run` created a run record in the DB but never called `WorkflowEngine.execute_run()`. A user hitting "Run" would see a pending run that sits there forever. Fixed: both `start_run_endpoint` and `webhook_trigger` now use `BackgroundTasks` to launch the engine after creating the run record. The response returns immediately with the run ID; execution happens asynchronously.

2. **Resume endpoint didn't complete the waiting step or re-invoke the engine.** It set the run status to "running" and emitted `RUN_RESUMED`, but the approval step was left in "waiting" status and nobody called `execute_run` to resume the loop. The engine's idempotent loop would see the waiting step and not know it was approved. Fixed: the endpoint now updates the waiting step_run to "completed" with the approval data, then launches the engine via BackgroundTasks. The engine picks up where it left off because it checks done_ids.

3. **Retry endpoint didn't reset the failed step or re-invoke the engine.** It just set the run to "pending" and returned. Nobody restarted execution, and the failed step_run record was still marked "failed" so the engine would skip it. Fixed: the endpoint now resets all failed step_runs to "pending" and launches the engine via BackgroundTasks.

4. **Catalog endpoint missing icon/category fields.** The spec defines `STEP_CATALOG` with `icon` and `category` for the frontend palette, but the catalog endpoint only returned `type`, `label`, `description`, `config_schema`. Fixed: added `STEP_CATALOG` to `registry.py` with all 12 step types including icon (Lucide icon names) and category (integrations/ai/logic/data/flow). Updated `StepTypeInfo` schema and `catalog.py` to merge catalog metadata with handler config_schema.

5. **`# type: ignore` in `workflows.py` and `executor.py`.** Non-negotiable violation. Fixed with proper None checks and control flow.

**What exists and is correct:**

- `workflows.py` — All 8 endpoints implemented correctly. Immutability enforcement on published workflows is correct. Duplicate creates new draft.
- `ws.py` — Snapshot-on-connect is implemented correctly (Pulse fixed the subscribe-before-snapshot race). Event streaming loop is clean.
- `schemas.py` — All Pydantic models are well-typed. Pulse already fixed the mutable default in WorkflowCreate.
- `router.py` — Clean aggregation of all sub-routers under `/api/v1`.
- `main.py` — FastAPI app with CORS, lifespan, health check. Correct structure.

**What's still missing (my domain):**

1. **Auth middleware not wired.** `dependencies.py` has `get_current_user` but no route uses it. Blocked on PM-01 Supabase Auth config (JWT secret needed).
2. **No pagination.** List endpoints return all rows. Need query params for page/per_page.
3. **BackgroundTasks vs ARQ.** Current fix uses FastAPI's `BackgroundTasks` which runs in the same process. For production, we need ARQ (Redis-backed) so execution survives worker restarts. Blocked on PM-01 Redis gate.
4. **No structured error responses.** Exceptions return FastAPI's default format. Need consistent error envelope.
5. **No rate limiting or request validation middleware.**

**Dependencies:**

- PM-01 (Axiom): Supabase Auth config (JWT secret) → unblocks auth middleware
- PM-01 (Axiom): Redis running → unblocks ARQ integration
- PM-02 (Forge): Engine is solid — `execute_run` works correctly for the happy path. The idempotent loop design means our background task approach works.
- PM-03 (Vertex): Step registry and catalog are correct. `STEP_CATALOG` is now defined in `registry.py`.
- Relay: WebSocket endpoint is correct. Snapshot-on-connect works.
- Pulse: Already fixed the subscribe/snapshot race and webhook idempotency. Good work.

**Axiom's work review:** Axiom wrote the initial API endpoints on their first shift. The routes are well-structured and thin. The critical gaps were all about the engine invocation — endpoints were "shape complete" but didn't actually trigger execution. Now they do.

### Architecture Decision: BackgroundTasks vs ARQ

For now, I'm using FastAPI's `BackgroundTasks` to launch the engine. This is the correct choice for Phase 1 because:
- It's zero-config — no Redis dependency needed
- It works for local dev immediately
- The engine loop is idempotent, so if the process dies mid-run, we can retry

For production (Phase 4), we switch to ARQ:
- Engine runs in a separate worker process
- Survives uvicorn restarts
- Run state in DB means we can recover

This is NOT a shortcut — it's the correct phased approach per the spec.

### Next Steps (Priority Order)

1. Add pagination to list endpoints (unblocked)
2. Add structured error response middleware (unblocked)
3. Wire auth middleware once PM-01 clears the Supabase Auth gate
4. Switch BackgroundTasks → ARQ once PM-01 clears the Redis gate
5. Write API tests using httpx.AsyncClient

---

## Outbox

**2026-02-24:**
- [x] Fixed trigger endpoints to actually launch the execution engine via BackgroundTasks — `backend/app/api/triggers.py`
- [x] Fixed resume endpoint to mark waiting step as completed + re-invoke engine — `backend/app/api/runs.py`
- [x] Fixed retry endpoint to reset failed step_runs + re-invoke engine — `backend/app/api/runs.py`
- [x] Added `STEP_CATALOG` with icon/category metadata for all 12 step types — `backend/app/steps/registry.py`
- [x] Updated catalog endpoint to return icon + category fields — `backend/app/api/catalog.py`
- [x] Updated `StepTypeInfo` schema with icon + category — `backend/app/db/schemas.py`
- [x] Removed `# type: ignore` from `workflows.py` (proper None guard) and `executor.py` (proper None check)
- [x] Signed roster as **Conduit — PM-04: API Layer & WebSocket**
- [!] FLAG: No API route currently uses authentication. `get_current_user` exists but is not wired into any `Depends()`. Blocked on PM-01 Supabase Auth gate.
- [!] FLAG: Engine invocation uses BackgroundTasks (in-process). Adequate for Phase 1 dev but must switch to ARQ for production. Blocked on PM-01 Redis gate.

**2026-02-23 (from Relay):**
- [x] D9 WebSocket — frontend side complete. `packages/shared/types/events.ts`, `runStore.ts`, `ws.ts`, `useRunStream.ts`, `RunDetail.tsx`, `ConnectionIndicator.tsx`, `RunOverlay.tsx` all rebuilt. Full event coverage, snapshot handling, reconnection. Mark D9 complete.
