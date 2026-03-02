# Next Priorities — Flow Matrx

**Date:** 2026-03-01  
**Status:** Engine + DB layer integration complete. 132 tests passing (all mocked — zero real DB coverage). System has not been tested against a live database. Type correctness in the DB/API boundary layer is unverified and likely has runtime failures.

---

## Priority 1: Fix Type Correctness in the DB/API Boundary (Blocking everything)

The core problem: `WfCore` mixes return types inconsistently and `_model_to_dict` is incomplete. When a real DB connection is active, these will produce runtime `TypeError` and Pydantic validation errors.

### 1a. Audit and fix `WfCore` return type consistency

**Decision to enforce:** `WfCore` methods used by the API layer always return Pydantic response models. Methods used only by the executor (`get_run`, `get_step_runs`, `get_workflow`) may return raw ORM models for efficiency, but must be clearly typed and documented.

Specific problems to fix in `app/db/custom/core.py`:

- `get_run` / `get_runs` / `create_run` / `update_run` use `item.__dict__` directly — but ORM model `__dict__` contains UUID objects (not strings), OpenDict instances, and FK proxy objects that Pydantic cannot validate without coercion
- `get_step_runs_for_run` uses `item.__dict__` — same problem; `StepRunResponse` expects `run_id: str` but ORM gives a UUID FK object
- `get_run_events` / `create_run_event` / `update_run_event` use `item.__dict__` — same FK/UUID issue
- `list_workflows_for_user` / `list_workflows_for_org` use `item.__dict__` — bypasses `_model_to_dict` which handles JSONB dataclasses
- `_model_to_dict` handles dataclass fields via `asdict()` but does NOT handle: UUID fields (need `str()`), FK fields (proxy objects), datetime fields, or `None` values from nullable fields

### 1b. Fix `_model_to_dict` to be a proper ORM→dict serializer

Must handle:
- UUID fields → `str(value)`
- FK fields (proxy objects) → `str(value.pk)` or just the FK id value
- Dataclass JSONB fields → `asdict(value)` but with care: `WfWorkflowInputSchema` serializes to `{"extra": {}}` when `WorkflowResponse.input_schema` expects `dict | None`
- Datetime fields → pass through (Pydantic handles these)
- `None` nullable fields → pass through

### 1c. Settle the JSONB type design

Currently `jsonb_types.py` has a mix:
- `WfWorkflowDefinition` is a proper dataclass (`.nodes`, `.edges`) — good
- `WfWorkflowInputSchema` is a dataclass with only `.extra: dict` — unclear value; API returns `dict | None`
- `WfRunInput`, `WfRunContext`, `WfRunEventPayload`, `WfStepRunInput`, `WfStepRunOutput` are all `OpenDict` aliases

**Decision needed:** For every JSONB field, decide: typed dataclass (strict fields) vs. OpenDict (pass-through). Current recommendation:
- `WfWorkflowDefinition` — keep as typed dataclass (`.nodes: list`, `.edges: list`)
- `WfWorkflowInputSchema` — change to `OpenDict` (it's user-defined JSON schema, open structure)
- `WfRunInput` / `WfRunContext` — keep as `OpenDict` (engine writes arbitrary step_id keys)
- `WfRunEventPayload` — keep as `OpenDict` (payload shape varies per event type)
- `WfStepRunInput` / `WfStepRunOutput` — keep as `OpenDict` (step-type-specific)

### 1d. Fix the executor's `get_run` return type

`execute_run` calls `wf_core.get_run(run_id)` and expects `.status`, `.workflow_id`, `.context`, `.input`. Currently `get_run` returns `RunResponse` (Pydantic), which works. But `run.context` is `dict[str, Any]` and `run.input` is `dict[str, Any]` in the schema — these need to actually be plain dicts, not OpenDict instances wrapped in a Pydantic model.

Verify: does Pydantic v2 validate `OpenDict` as `dict[str, Any]`? It should, since `OpenDict` is a `dict` subclass. Confirm this is safe.

---

## Priority 2: Unit Tests for the DB Layer (With a Real or Faked Connection)

All current 132 tests mock the DB entirely. We have zero coverage of:
- Whether `_model_to_dict` produces valid input for Pydantic models
- Whether ORM model fields serialize correctly (UUID, datetime, FK proxies)
- Whether `WfCore` methods produce the right output shapes

### 2a. Write unit tests for `_model_to_dict` with fake ORM model instances

Create fake ORM instances that mimic the field types the real ORM returns (UUID objects, FK proxies, OpenDict, WfWorkflowDefinition dataclass) and assert that `_model_to_dict` + Pydantic validation succeeds.

### 2b. Write unit tests for every `WfCore` method

Mock the underlying managers (`self.workflows`, `self.runs`, etc.) at the `WfCore` level — not at the raw DB level — and verify that every public method returns the declared return type with correct field values.

### 2c. Write unit tests for the executor with properly typed fakes

The current `test_executor.py` uses `FakeRun` / `FakeWorkflow` / `FakeStepRun` objects. Verify these match the actual attribute shapes that the executor accesses:
- `run.status`, `run.workflow_id`, `run.context`, `run.input` — match `RunResponse`
- `workflow.definition.nodes`, `workflow.definition.edges` — match `WfWorkflow.definition`
- `sr.status`, `sr.step_id`, `sr.id` — match `WfStepRun`

---

## Priority 3: API Route Tests

After the DB layer is correct, test every FastAPI endpoint:
- Request → validated → `wf_core` call → response shape
- Error cases: 404 (not found), 409 (state conflicts), 422 (validation failures)
- Use FastAPI `TestClient` with `wf_core` mocked at the module level

---

## Priority 4: Live Database Smoke Test

Only attempt after Priorities 1–3 are green.

- Run `scripts/schema.sql` against Supabase
- Confirm ORM models match schema (reverse migration check)
- `POST /api/v1/workflows` → create workflow
- `POST /api/v1/workflows/{id}/publish`
- `POST /api/v1/workflows/{id}/run` → triggers engine
- `GET /api/v1/runs/{id}` → verify completed with context
- `WS /ws/runs/{id}` → verify snapshot + event stream

---

## Priority 5: Frontend (After Backend is Verified)

Frontend already scaffolded but has TypeScript build errors (BaseNode type mismatch in `@xyflow/react` NodeProps, and API client URLs don't match backend routes). Do not invest here until backend is fully verified.

- Fix `BaseNode.tsx` type: add index signature to `BaseNodeData`
- Align `src/api/runs.ts` URL patterns with actual FastAPI routes
- Fix `src/api/workflows.ts` URL patterns

---

## Known Gaps (Track, don't fix yet)

| Gap | When to fix |
|-----|-------------|
| Auth: no Supabase JWT wired to FastAPI | After smoke test passes |
| `created_by` / `org_id` / `user_id` hardcoded or missing | After auth integration |
| `send_email` handler is a placeholder | When email infra is ready |
| No rate limiting on API endpoints | Before production |
| No WebSocket authentication | Before production |
| Function registry: no arg-level schema enforcement | Priority 5b (original) |
| Scheduled/webhook triggers (ARQ) | After frontend foundation |
