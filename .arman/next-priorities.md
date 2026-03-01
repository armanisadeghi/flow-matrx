# Next Priorities — Flow Matrx

**Date:** 2026-03-01
**Status after engine core:** Phase 1 complete. Engine can execute complex DAGs with parallel steps, conditions, pausing, retries, for_each, registered functions, and real-time events. 132 tests passing.

---

## Priority 1: Database & Backend Online (Blocking everything else)

### 1a. Create the database
- Run `scripts/schema.sql` against your Supabase instance
- Verify all 4 tables, indexes, triggers, and CHECK constraints are live
- The schema is final — the SQL file is the source of truth

### 1b. Verify Matrx-ORM models match the schema
- Run Matrx-ORM reverse migration to regenerate `db/models.py`
- Confirm `runs.created_by` column exists (newly added)
- Test a round-trip: create workflow → start run → verify step_runs + run_events populate

### 1c. Write the first Alembic migration
- `alembic init` if not already done
- Migration 001 should match `scripts/schema.sql` exactly
- This is the baseline — all future changes go through Alembic

---

## Priority 2: End-to-End Smoke Test (Proves the engine works for real)

### 2a. Seed a real workflow
- Use `scripts/seed-workflow.py` (already exists) to insert the sample HTTP + LLM workflow
- Or create a simpler 3-step transform-only workflow for testing without external deps

### 2b. Trigger a run via the API
- `POST /api/v1/workflows/{id}/run` with `{"input": {...}}`
- Verify the engine executes, populates step_runs, emits events
- Check `GET /api/v1/runs/{id}` returns completed status with full context

### 2c. Test the WebSocket
- Connect to `WS /ws/runs/{id}` during execution
- Verify snapshot arrives on connect, then live events stream

### 2d. Test pause/resume
- Create a workflow with a `wait_for_approval` step
- Trigger run → verify it pauses
- Call `POST /api/v1/runs/{id}/resume` → verify it continues to completion

---

## Priority 3: Frontend Foundation

### 3a. Project scaffolding
- Vite + React 19 + TypeScript strict mode
- Tailwind 4.2 + shadcn/ui setup
- React Router with SPA mode
- Zustand store skeleton
- TanStack Query configuration pointing at backend

### 3b. Workflow canvas (React Flow)
- Drag-and-drop step palette (sourced from `GET /api/v1/catalog/steps`)
- Node components for each step type (at minimum: transform, http_request, condition)
- Edge connections with condition labels on sourceHandle
- Save/load workflow definition to/from API

### 3c. Config panels
- Side panel that opens when a node is selected
- Form fields generated from the step's `config_schema`
- Template autocompletion (suggest `{{upstream_step.field}}` based on graph)

---

## Priority 4: Live Run Visualization

### 4a. Run viewer component
- Subscribe to WebSocket for run ID
- Render the workflow graph with live status colors per node
- Show step output in a detail panel when a node is clicked

### 4b. Approval flow UI
- Detect `step.waiting` events
- Show an approval dialog with the prompt text
- POST resume on approval

### 4c. Run history page
- List all runs with status, duration, trigger type
- Click to open the run viewer for replay

---

## Priority 5: Hardening & Production Features

### 5a. Auth integration
- Wire Supabase JWT auth to FastAPI
- Populate `workflows.created_by` and `runs.created_by` from JWT
- Inject `context["_user"]` so registered functions can access user info

### 5b. Function registry loading from config
- Load registered functions at startup from a config file or DB table
- Add `GET /api/v1/catalog/functions` endpoint
- Optional: schema validation of function args at registration time

### 5c. Scheduled and webhook triggers
- ARQ job for scheduled workflow execution
- `POST /api/v1/triggers/webhook/{workflow_id}` endpoint
- `runs.trigger_type` already supports these values

### 5d. Workflow versioning UI
- Show version history
- Diff between versions
- "Duplicate as new draft" flow

### 5e. Production deployment
- Docker images for backend
- Vercel/Cloudflare deployment for frontend
- Environment variable management
- Health check endpoint

---

## Known Gaps (Not blocking, but track them)

| Gap | Impact | When to fix |
|-----|--------|-------------|
| Registered functions have no arg-level schema enforcement | Runtime errors on bad args | Priority 5b |
| Registered functions cannot access user info | No user-aware custom functions | Priority 5a |
| Registered functions cannot emit progress events | No mid-step streaming | Future: add optional callback param |
| `send_email` handler is a placeholder | Email step doesn't actually send | When email infra is ready |
| No rate limiting on API endpoints | Abuse risk in production | Priority 5e |
| No WebSocket authentication | Anyone with a run ID can subscribe | Priority 5a |
| `step_runs` grows unbounded for high-retry workflows | Storage bloat | Add TTL/archival policy later |
