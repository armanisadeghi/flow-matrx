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
