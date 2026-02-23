# CLAUDE.md — Flow Matrx Workflow Engine

**Product:** Visual workflow builder and execution engine for AI Matrx
**Owner:** Arman (Armani) Sadeghi

---

## What This Is

A visual drag-and-drop workflow builder where users create DAGs of steps on a React Flow canvas, then execute them via a Python async engine with real-time WebSocket streaming of every state transition. Three concerns are surgically separated: **Definition** (React Flow canvas), **Execution** (Python FastAPI engine), **State** (PostgreSQL).

---

## Monorepo Layout

```
flow-matrx/
├── backend/          Python FastAPI execution engine (uv)
├── frontend/         React 19 + Vite SPA (pnpm)
├── packages/shared/  Shared TypeScript types
├── scripts/          Seed data and migration helpers
└── docker-compose.yml
```

- No cross-imports between frontend/ and backend/. Shared code lives in packages/shared/ only.
- Backend has zero JS deps. Frontend has zero Python deps.

---

## Tech Stack (Locked Versions)

### Backend
- **Python 3.14** | **FastAPI 0.131** | **Matrx-ORM 2.0.10** | **asyncpg 0.31**
- **uv** for all package management (no pip, no poetry)
- **Pydantic 2.12** for validation | **structlog 24.4** for logging
- **Alembic 1.18** for migrations | **ARQ 0.27** + Redis for background tasks
- **httpx 0.28** for async HTTP | **Jinja2 3.1** for template resolution
- **orjson 3.11** for fast JSON

### Frontend
- **React 19** | **Vite 7.3** | **TypeScript 5.9** (strict mode)
- **@xyflow/react 12.10** (React Flow v12 — NOT legacy `reactflow` package)
- **Tailwind CSS 4.2** (CSS-first config, NO tailwind.config.js)
- **shadcn/ui** (all UI primitives) | **Lucide React** (icons)
- **Zustand 5.0** (client state) | **TanStack React Query 5.90** (server state)
- **React Router 7.13** (SPA mode) | **React Hook Form 7.54** + **Zod 3.24**
- **Monaco Editor 4.6** | **dagre 1.1** (auto-layout)
- **Biome 1.9** for linting/formatting (NOT ESLint/Prettier)
- **pnpm** for all package management (no npm, no yarn)

### Explicitly Banned
Redux, Axios, styled-components, CSS modules, Moment.js, Lodash (full), Jotai/Recoil/Valtio/MobX, Ant Design/Material UI/Chakra UI, Jest, ESLint+Prettier.

### Infrastructure
- PostgreSQL 18 (Supabase-hosted) | Redis 8 (task queue + pub/sub)
- Docker Compose for local dev
- Vercel/Cloudflare Pages (frontend) | Coolify/Railway/VPS (backend)

---

## Core Architecture

### Database (4 tables)
- **workflows** — DAG definitions (JSONB nodes + edges from React Flow, stored verbatim)
- **runs** — Execution instances with status, input, accumulated context
- **step_runs** — Individual step execution records with resolved input and output
- **run_events** — Append-only event log (source of truth for audit/replay/WebSocket)

### Execution Engine
The engine loop: build graph -> find ready steps (deps satisfied) -> execute in parallel via `asyncio.gather` -> update context -> broadcast events -> repeat until done/paused/failed. The loop is idempotent — calling it on a partially-completed run picks up where it left off.

### Communication Protocol
- **Event Bus** — In-process pub/sub. Engine emits events at every state transition.
- **WebSocket** `/ws/runs/{id}` — Sends snapshot on connect, then streams live events.
- **Event types:** run.started, run.completed, run.failed, run.paused, run.resumed, run.cancelled, step.started, step.completed, step.failed, step.skipped, step.waiting, step.retrying, context.updated
- Events are facts. The UI renders facts. NO polling. NO inference.

### Step Handler Plugin System
- Base class: `StepHandler` with `execute(config, context) -> dict`
- Handlers are pure functions — no DB writes, no event emission, no run awareness
- Registry: `STEP_REGISTRY = {"type_name": HandlerInstance()}`
- Types: http_request, llm_call, inline_code, condition, database_query, transform, delay, wait_for_approval, send_email, webhook, wait_for_event, for_each
- Adding a step = 5 files: Python handler, registry entry, React node, React config panel, frontend registry entries

### Data Flow Between Steps
- All data passes through `runs.context` (shared scratchpad)
- Steps reference upstream data via `{{context.step_id.field}}` templates
- No "data wires" or connection-level mapping in the UI
- `step_runs.input` stores RESOLVED config (templates filled in) for debugging

---

## Non-Negotiables

1. React Flow graph IS the workflow definition — no translation layer, no YAML, no DSL
2. All inter-step data flows through context — no data wires
3. Events are the ONLY mechanism for real-time updates — NEVER poll
4. Step handlers are pure functions — engine handles DB/events/retries
5. No `any` types in TypeScript — use `unknown` then narrow
6. No `# type: ignore` in Python
7. No business logic in API routes (under 20 lines each)
8. No circular imports
9. Every DB query is parameterized — no string interpolation in SQL
10. Every state transition emits exactly one event with the documented payload shape
11. WebSocket sends snapshot on connect (for late joiners/reconnection)
12. Node status uses ONLY WebSocket events — no API calls during runs
13. Every step type has exactly 3 artifacts: Python handler, React node, React config panel
14. No inline styles — Tailwind only. Only CSS file is index.css
15. All UI primitives from shadcn/ui — no custom base components
16. Workflow definitions immutable once published — edit creates new version
17. run_events is append-only — never update or delete
18. Use `uv` for Python, `pnpm` for frontend, Biome for lint/format

---

## API Endpoints

### Workflows
- `GET/POST /api/v1/workflows` — List / Create
- `GET/PUT/DELETE /api/v1/workflows/{id}` — Read / Update draft / Delete draft
- `POST /api/v1/workflows/{id}/publish` — Freeze definition
- `POST /api/v1/workflows/{id}/validate` — Check for errors
- `POST /api/v1/workflows/{id}/duplicate` — Copy as new draft

### Runs
- `POST /api/v1/workflows/{id}/run` — Start execution
- `GET /api/v1/runs` — List (filter by workflow_id, status, date)
- `GET /api/v1/runs/{id}` — Status + context + timing
- `GET /api/v1/runs/{id}/steps` — All step_runs
- `GET /api/v1/runs/{id}/events` — All events (for replay)
- `POST /api/v1/runs/{id}/resume` — Resume paused run
- `POST /api/v1/runs/{id}/cancel` — Cancel
- `POST /api/v1/runs/{id}/retry` — Retry from failed step

### Other
- `WS /ws/runs/{id}` — Live event stream
- `GET /api/v1/catalog/steps` — Step type metadata for palette

All resource-creating endpoints MUST support `X-Idempotency-Key` header.

---

## Development Commands

```bash
# Local dev stack (Docker)
make dev                    # docker-compose up (Postgres, Redis, backend, frontend)
make stop                   # docker-compose down

# Backend (from backend/)
uv sync                     # Install deps
uv run uvicorn app.main:app --reload --port 8000  # Run server
uv run pytest tests/ -v     # Run tests
alembic upgrade head        # Run migrations

# Frontend (from frontend/)
pnpm install                # Install deps
pnpm dev                    # Vite dev server (port 5173)
pnpm build                  # Production build
pnpm test                   # Vitest
pnpm biome check --write src  # Lint + format

# Seed data
make seed                   # Insert sample workflows
```

---

## Phase Plan

1. **Phase 1 (Foundation):** Engine executes linear workflow with 3 step types + WebSocket streaming
2. **Phase 2 (Builder):** Visual canvas with drag-drop, config panels, save/load/publish
3. **Phase 3 (Live Execution):** Real-time run visualization, approval flow, run history
4. **Phase 4 (Polish):** Versioning, scheduled/webhook triggers, auto-layout, full tests, production deploy

---

## Code Standards

- TypeScript strict mode — no `any`, use generics and discriminated unions
- Python: full type hints, Pydantic models, no docstrings required
- Error handling on every API call, DB query, and async operation
- Validate at system boundaries only — trust internal code
- Don't add comments/docstrings/types to unchanged code
- Three similar lines > premature abstraction
- Fix bugs, don't refactor surrounding code
