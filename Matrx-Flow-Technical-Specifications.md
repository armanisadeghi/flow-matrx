# Matrx Flow Technical Specification

**Document Version:** 1.2
**Date:** February 23, 2026
**Status:** Ready for Implementation
**Author:** Architecture Team
**Package Managers:** `uv` (Python) / `pnpm` (Frontend)
**ORM:** Matrx-ORM v2.0.10

---

## Table of Contents

1. [Vision & Architecture](#1-vision--architecture)
2. [Monorepo Structure](#2-monorepo-structure)
3. [Technology Stack — Locked Versions](#3-technology-stack--locked-versions)
4. [Team Assignments](#4-team-assignments)
5. [Database Schema & Conventions](#5-database-schema--conventions)
6. [Communication Protocol — First Class](#6-communication-protocol--first-class)
7. [Python Backend — Execution Engine](#7-python-backend--execution-engine)
8. [Step Handler System — The Plugin Architecture](#8-step-handler-system--the-plugin-architecture)
9. [API Layer](#9-api-layer)
10. [Frontend — React + Vite + React Flow](#10-frontend--react--vite--react-flow)
11. [UI/UX Standards](#11-uiux-standards)
12. [Non-Negotiables](#12-non-negotiables)
13. [Testing Requirements](#13-testing-requirements)
14. [Deployment & Infrastructure](#14-deployment--infrastructure)
15. [Phase Plan](#15-phase-plan)

---

## 1. Vision & Architecture

### What We Are Building

A visual workflow builder and execution engine for AI Matrx. Users drag and drop steps on a canvas to create workflows. The system executes those workflows with full support for parallel execution, conditional branching, human-in-the-loop approvals, and real-time visibility into every step as it runs.

### The Core Principle

**Three things, kept surgically separated:**

| Concern | Artifact | Owner |
|---------|----------|-------|
| **Definition** | The workflow graph (nodes + edges) | React Flow canvas |
| **Execution** | The engine that walks the graph | Python FastAPI service |
| **State** | Run status, step outputs, context | PostgreSQL |

If you ever find yourself mixing these — stop. That is where every workflow system goes wrong.

### The Architecture

```
┌──────────────────────────────────────────────────────────┐
│                      Frontend SPA                         │
│               React 19 + Vite + React Flow                │
│                                                           │
│   Canvas (builder) ←→ Run Viewer (live) ←→ Dashboard      │
│                                                           │
│   Deployed as static files (Vercel / Cloudflare Pages)    │
└────────────────┬───────────────┬──────────────────────────┘
                 │ REST          │ WebSocket
                 │               │
┌────────────────▼───────────────▼──────────────────────────┐
│                   Workflow Service                         │
│                   FastAPI (Python)                         │
│                                                           │
│   ┌─────────────────────────────────────────────┐         │
│   │           Execution Engine                   │         │
│   │  while ready_steps:                          │         │
│   │      parallel_execute(ready_steps)           │         │
│   │      update_context()                        │         │
│   │      broadcast_events()        ◄── THIS LOOP │         │
│   └─────────────────────────────────────────────┘         │
│                                                           │
│   Step Registry: {type → handler}                         │
│   Event Bus: step status → WebSocket broadcast            │
│                                                           │
│   Direct access to:                                       │
│   ├── AI Matrx LLM packages (in-process)                  │
│   ├── AI Matrx Python microservices (HTTP)                │
│   └── PostgreSQL (via Matrx-ORM + asyncpg)               │
└────────────────────────┬──────────────────────────────────┘
                         │
┌────────────────────────▼──────────────────────────────────┐
│                     PostgreSQL                             │
│              (Supabase-hosted instance)                    │
│                                                           │
│   workflows │ runs │ step_runs │ run_events                │
│                                                           │
│   Auth: Supabase Auth (JWT) for frontend                  │
│   Engine: Matrx-ORM with asyncpg (bypass PostgREST)      │
└───────────────────────────────────────────────────────────┘
```

### Why This Stack (Not Negotiable)

| Decision | Reason |
|----------|--------|
| **Python for engine** | Workflow runs are long-lived processes. `asyncio.gather` gives parallel step execution in one line. All AI Matrx LLM packages and heavy compute are Python. Zero translation hops. |
| **FastAPI** | Native async, native WebSocket, native background tasks, Pydantic validation, OpenAPI docs auto-generated. |
| **Matrx-ORM** | Our custom ORM with reverse migrations, auto-generated Model Manager classes, and full async support via asyncpg. Superior to SQLAlchemy/Tortoise for our patterns. |
| **uv** | Python package manager. Blazing fast, deterministic lockfiles, replaces pip/pip-tools/poetry. All backend dependency management goes through `uv`. |
| **React + Vite (NOT Next.js)** | The builder is an SPA — no SEO, no SSR, no static generation needed. Vite is faster in every measurable way. No hydration bugs with React Flow. Per AI Matrx Frontend Standards: "Use Vite (SPA) when the app is fully authenticated and you're building an internal tool." |
| **pnpm** | Frontend package manager. Strict, fast, disk-efficient. All frontend dependency management goes through `pnpm`. |
| **Supabase PostgreSQL** | Hosted Postgres with auth, realtime subscriptions as backup channel, and the database UI for quick debugging. Engine connects via Matrx-ORM for performance. |
| **Monorepo** | Frontend and backend live together. Shared types. One PR for a feature. One deploy pipeline. |

---

## 2. Monorepo Structure

```
ai-matrx-workflow/
│
├── README.md
├── docker-compose.yml              # Local dev: Postgres + backend + frontend
├── .env.example
├── Makefile                         # Common commands: make dev, make test, make migrate (delegates to uv/pnpm)
│
├── packages/
│   └── shared/                      # Shared types between frontend and backend
│       ├── types/
│       │   ├── workflow.ts          # WorkflowDefinition, Node, Edge types
│       │   ├── run.ts               # Run, StepRun, RunStatus types
│       │   └── events.ts           # WebSocket event types
│       └── package.json
│
├── backend/
│   ├── pyproject.toml               # Python project config (managed with uv)
│   ├── uv.lock                      # uv lockfile (committed to git)
│   ├── alembic.ini                  # Database migrations
│   ├── alembic/
│   │   └── versions/                # Migration files
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app, startup, shutdown, middleware
│   │   ├── config.py                # Settings from env vars (pydantic-settings)
│   │   ├── dependencies.py          # Dependency injection (db, engine, auth)
│   │   │
│   │   ├── engine/
│   │   │   ├── __init__.py
│   │   │   ├── executor.py          # WorkflowEngine — the execution loop
│   │   │   ├── graph.py             # Graph helper (adjacency, ready steps, branches)
│   │   │   ├── templates.py         # {{template}} resolution
│   │   │   ├── safe_eval.py         # Sandboxed expression evaluation
│   │   │   └── exceptions.py        # PauseExecution, StepTimeout, etc.
│   │   │
│   │   ├── steps/
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # StepHandler ABC
│   │   │   ├── registry.py          # STEP_REGISTRY dict
│   │   │   ├── http_request.py
│   │   │   ├── llm_call.py
│   │   │   ├── inline_code.py
│   │   │   ├── condition.py         # (engine-handled, but config schema lives here)
│   │   │   ├── database_query.py
│   │   │   ├── transform.py
│   │   │   ├── wait_for_approval.py
│   │   │   ├── wait_for_event.py
│   │   │   ├── send_email.py
│   │   │   ├── webhook.py
│   │   │   ├── delay.py
│   │   │   └── for_each.py          # Loop/iteration step
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── router.py            # Main router that includes all sub-routers
│   │   │   ├── workflows.py         # CRUD endpoints
│   │   │   ├── runs.py              # Execute, status, resume, cancel
│   │   │   ├── triggers.py          # Webhook + schedule endpoints
│   │   │   └── ws.py                # WebSocket endpoint for run streaming
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── connection.py        # Matrx-ORM connection + asyncpg pool setup
│   │   │   ├── models/              # Matrx-ORM model definitions
│   │   │   │   ├── __init__.py
│   │   │   │   ├── workflow.py      # Workflow model
│   │   │   │   ├── run.py           # Run model
│   │   │   │   ├── step_run.py      # StepRun model
│   │   │   │   └── run_event.py     # RunEvent model
│   │   │   ├── queries/
│   │   │   │   ├── workflows.py     # Workflow CRUD queries
│   │   │   │   ├── runs.py          # Run CRUD + state queries
│   │   │   │   └── step_runs.py     # Step run queries
│   │   │   └── schemas.py           # Pydantic models for API request/response
│   │   │
│   │   ├── events/
│   │   │   ├── __init__.py
│   │   │   ├── bus.py               # In-process event bus
│   │   │   └── types.py             # Event type definitions
│   │   │
│   │   ├── validation/
│   │   │   ├── __init__.py
│   │   │   └── workflow.py          # DAG validation, template ref checking
│   │   │
│   │   └── auth/
│   │       ├── __init__.py
│   │       └── jwt.py               # Supabase JWT verification
│   │
│   └── tests/
│       ├── conftest.py
│       ├── test_engine/
│       ├── test_steps/
│       ├── test_api/
│       └── test_validation/
│
├── frontend/
│   ├── package.json
│   ├── pnpm-lock.yaml               # pnpm lockfile (committed to git)
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── biome.json                    # Biome linter + formatter config (replaces ESLint + Prettier)
│   ├── components.json               # shadcn/ui configuration
│   ├── index.html
│   │
│   ├── src/
│   │   ├── main.tsx                 # App entry
│   │   ├── App.tsx                  # Router setup
│   │   ├── index.css                # Tailwind v4 CSS-first config (@import "tailwindcss" + @theme)
│   │   │
│   │   ├── api/
│   │   │   ├── client.ts            # Base fetch wrapper with auth
│   │   │   ├── workflows.ts         # Workflow CRUD
│   │   │   ├── runs.ts              # Run management
│   │   │   └── ws.ts                # WebSocket connection manager
│   │   │
│   │   ├── stores/
│   │   │   ├── workflowStore.ts     # Zustand store for canvas state
│   │   │   └── runStore.ts          # Zustand store for active run state
│   │   │
│   │   ├── pages/
│   │   │   ├── WorkflowList.tsx     # Dashboard: all workflows
│   │   │   ├── WorkflowBuilder.tsx  # The canvas page
│   │   │   ├── RunHistory.tsx       # All runs for a workflow
│   │   │   └── RunDetail.tsx        # Single run deep-dive
│   │   │
│   │   ├── components/
│   │   │   ├── canvas/
│   │   │   │   ├── Canvas.tsx       # React Flow wrapper
│   │   │   │   ├── StepPalette.tsx  # Draggable step types
│   │   │   │   ├── NodeConfigPanel.tsx  # Right-side config editor
│   │   │   │   └── EdgeLabel.tsx    # Condition labels on edges
│   │   │   │
│   │   │   ├── run/
│   │   │   │   ├── RunOverlay.tsx   # Live status overlay on canvas
│   │   │   │   ├── StepOutput.tsx   # Output viewer per step
│   │   │   │   └── RunControls.tsx  # Start, pause, cancel, resume
│   │   │   │
│   │   │   └── shared/
│   │   │       ├── TemplateInput.tsx    # Input with {{}} autocomplete
│   │   │       ├── CodeEditor.tsx       # Monaco-based editor
│   │   │       └── StatusBadge.tsx
│   │   │
│   │   ├── components/ui/             # shadcn/ui components (auto-generated, do not hand-edit)
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── select.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── dropdown-menu.tsx
│   │   │   ├── tooltip.tsx
│   │   │   ├── badge.tsx
│   │   │   └── ... (added via `pnpm dlx shadcn@latest add <component>`)
│   │   │
│   │   ├── nodes/                   # One component per step type
│   │   │   ├── BaseNode.tsx         # Shared node shell (handles, status ring)
│   │   │   ├── HttpRequestNode.tsx
│   │   │   ├── LLMCallNode.tsx
│   │   │   ├── ConditionNode.tsx
│   │   │   ├── InlineCodeNode.tsx
│   │   │   ├── DatabaseQueryNode.tsx
│   │   │   ├── ApprovalNode.tsx
│   │   │   ├── DelayNode.tsx
│   │   │   └── index.ts            # nodeTypes registry export
│   │   │
│   │   ├── config-panels/          # One config form per step type
│   │   │   ├── HttpRequestConfig.tsx
│   │   │   ├── LLMCallConfig.tsx
│   │   │   ├── ConditionConfig.tsx
│   │   │   ├── InlineCodeConfig.tsx
│   │   │   ├── DatabaseQueryConfig.tsx
│   │   │   ├── ApprovalConfig.tsx
│   │   │   └── index.ts            # configPanels registry export
│   │   │
│   │   ├── hooks/
│   │   │   ├── useRunStream.ts      # WebSocket hook for live updates
│   │   │   ├── useWorkflow.ts       # CRUD operations
│   │   │   ├── useAutoLayout.ts     # dagre-based auto-layout
│   │   │   └── useValidation.ts     # Client-side graph validation
│   │   │
│   │   ├── lib/
│   │   │   ├── utils.ts             # cn() utility (clsx + tailwind-merge)
│   │   │   ├── constants.ts
│   │   │   ├── templates.ts         # Template parsing for autocomplete
│   │   │   └── graph-utils.ts       # Upstream/downstream helpers
│   │   │
│   │   └── types/
│   │       └── index.ts             # Re-export from shared package
│   │
│   └── public/
│       └── favicon.svg
│
└── scripts/
    ├── seed-workflow.py              # Insert sample workflows for dev
    └── run-migration.sh
```

### Rules for Monorepo Organization

1. **No cross-imports between frontend/ and backend/.** The only shared code lives in `packages/shared/`.
2. **Every step type has exactly three files:** a Python handler, a React node component, and a React config panel. Always add all three together.
3. **No barrel files that re-export everything.** Import from specific modules.
4. **Backend has zero JavaScript dependencies.** Frontend has zero Python dependencies.

---

## 3. Technology Stack — Locked Versions

These are the exact versions to install. Do not use older versions. Do not substitute alternatives without architecture team approval.

### Backend

| Package | Version | Purpose |
|---------|---------|---------|
| Python | 3.14.x | Runtime. Python 3.14 (released Oct 2025) is required. |
| uv | latest | Package manager. All Python deps installed via `uv add`. |
| Matrx-ORM | 2.0.10 | AI Matrx custom ORM. Reverse migrations, Model Manager classes, full async via asyncpg. |
| FastAPI | 0.131.x | API framework |
| uvicorn | 0.41.x | ASGI server |
| asyncpg | 0.31.x | PostgreSQL async driver (used by Matrx-ORM under the hood) |
| pydantic | 2.12.x | Validation and serialization |
| pydantic-settings | 2.13.x | Environment config |
| httpx | 0.28.x | Async HTTP client (for step handlers) |
| structlog | 24.4.x | Structured logging |
| alembic | 1.18.x | Database migrations |
| arq | 0.27.x | Background task queue (Redis-backed) |
| jinja2 | 3.1.x | Template resolution in step configs |
| orjson | 3.11.x | Fast JSON serialization |

**Python 3.14 Note:** Python 3.14 has significantly improved support for PEP 734 (Multiple Interpreters / Subinterpreters). Consider using subinterpreters for the `inline_code` step handler to provide better isolation than standard `asyncio`. Evaluate during Phase 1.

### Frontend

| Package | Version | Purpose |
|---------|---------|---------|
| React | 19.0.x | UI library |
| Vite | 7.3.x | Build tool and dev server |
| pnpm | 9.x | Package manager. All frontend deps installed via `pnpm add`. |
| @xyflow/react | 12.10.x | React Flow (canvas library). NOTE: Always use `@xyflow/react`, NOT the legacy `reactflow` package. v12 is a significant departure from v11 — see note below. |
| TypeScript | 5.9.x | Type safety. `strict: true` is mandatory. See TS 6/7 note below. |
| Tailwind CSS | 4.2.x | Styling. v4 uses CSS-first config — NO `tailwind.config.js`. See Tailwind v4 note below. |
| zustand | 5.0.x | Client state management (run status, UI state) |
| @tanstack/react-query | 5.90.x | Server state management (API data fetching, caching) |
| @tanstack/query-devtools | 5.90.x | Visual cache inspector. Install on every project from day one. |
| react-hook-form | 7.54.x | Form state management (config panels) |
| zod | 3.24.x | Schema validation and TypeScript type inference |
| @monaco-editor/react | 4.6.x | Code editor for inline code steps |
| dagre | 1.1.x | Auto-layout algorithm for the canvas |
| react-router | 7.13.x | Routing (SPA mode, not Framework Mode for this project) |
| lucide-react | 0.575.x | Icons. This is what shadcn/ui uses — do NOT mix icon libraries. |
| shadcn/ui | latest CLI | Component primitives (copied into project, not a dependency). Initialized via `pnpm dlx shadcn@latest init`. |
| clsx + tailwind-merge | latest | Class name composition via the `cn()` utility function |
| sonner | latest | Toast notifications (shadcn/ui recommended) |
| motion | 12.3.x | Animation library (formerly Framer Motion). Use ONLY for animations beyond CSS capability. |
| date-fns | 4.1.x | Date manipulation. Tree-shakeable, v4 includes timezone support. |
| biome | 1.9.x | Linting and formatting (replaces ESLint + Prettier). Written in Rust. |

**Tailwind CSS v4 Note:** Tailwind v4 uses a high-performance Rust engine and CSS-first configuration. There is NO `tailwind.config.js` or `tailwind.config.ts`. Configuration is done in CSS:

```css
/* src/index.css */
@import "tailwindcss";

@theme {
  --color-brand: #your-color;
  --font-sans: "Inter", sans-serif;
}
```

**shadcn/ui Note:** As of 2026, shadcn/ui uses a unified `radix-ui` package. Components are owned code — copied into `src/components/ui/`, not installed as a dependency. Every UI primitive (Button, Input, Select, Dialog, etc.) comes from shadcn. Do NOT use Ant Design, Material UI, or Chakra UI.

**React Flow v12 Note:** Version 12 of `@xyflow/react` introduces "measured" node dimensions — the library measures actual DOM elements rather than relying on pre-declared width/height. This affects how you handle node sizing and auto-layout with dagre. Always let React Flow measure nodes rather than hardcoding sizes. When using dagre for auto-layout, read measured dimensions from the React Flow instance after initial render, not before.

**TypeScript 6/7 Note:** TypeScript 6 is the transition release before the Go-based rewrite in TypeScript 7. TS 6 enforces `strict: true` by default, which aligns with our Non-Negotiables. Stick with 5.9.x for stability now. When TS 6 reaches stable (expected mid-2026), evaluate upgrading — the stricter defaults will be a no-op for us since we already enforce strict mode.

### Explicitly Excluded (Frontend)

Per AI Matrx Frontend Standards, these are **not permitted** on this project:

| Technology | Reason |
|:---|:---|
| **Redux / Redux Toolkit** | TanStack Query + Zustand covers all use cases. |
| **Axios** | Native `fetch` is sufficient. TanStack Query handles retry and caching. |
| **Styled Components / Emotion / CSS Modules** | Tailwind CSS is the standard. No mixed styling. |
| **Moment.js** | Deprecated. Use date-fns. |
| **Lodash** (full import) | Most utilities are native JS. Import individual functions from `lodash-es` if needed. |
| **Jotai / Recoil / Valtio / MobX** | Zustand is the standard. One state library. |
| **Ant Design / Material UI / Chakra UI** | shadcn/ui + Radix is the component standard. |
| **Jest** | Use Vitest. Faster, natively understands ESM and Vite config. |
| **ESLint + Prettier** | Use Biome. Single tool, written in Rust, dramatically faster. |

### Infrastructure

| Tool | Version | Purpose |
|------|---------|---------|
| PostgreSQL | 18.x | Primary database (Supabase-hosted). Note: 18.3 scheduled for Feb 26, 2026 fixes a `substring()` regression in 18.2. |
| Redis | 8.0.x | Background task queue + pub/sub for events |
| Docker + Docker Compose | latest | Local development |
| Supabase | latest | Auth (JWT), hosted Postgres, dashboard |

---

## 4. Team Assignments

The project requires three specialist tracks executing in parallel after the shared foundation is established.

### Track 1: Database & Infrastructure Engineer

**Owns:** Schema, migrations, Docker setup, deployment config, Redis setup.

**Deliverables (in order):**

1. Set up the Supabase project and configure the Postgres instance.
2. Write and run ALL migrations defined in Section 5 using Alembic.
3. Create `docker-compose.yml` for local dev (Postgres, Redis, backend, frontend).
4. Set up Redis instance for background task queue.
5. Configure Supabase Auth with JWT verification for the API.
6. Create database indexes as specified in Section 5.
7. Write the `seed-workflow.py` script that inserts 2-3 sample workflows for development.

**Skills required:** PostgreSQL, Docker, Supabase, Redis, basic Python.

### Track 2: Python Backend Engineer

**Owns:** FastAPI service, execution engine, step handlers, WebSocket streaming, API endpoints.

**Deliverables (in order):**

1. Scaffold the FastAPI application with project structure from Section 2.
2. Implement the database connection layer (Matrx-ORM with asyncpg pool).
3. Implement the **Event Bus** (Section 6) — this comes BEFORE the engine.
4. Implement the **Graph** utility class (Section 7).
5. Implement the **Template Resolution** system (Section 7).
6. Implement the **Workflow Validation** system (Section 7).
7. Implement the **Execution Engine** (Section 7) — the core loop.
8. Implement ALL step handlers defined in Section 8.
9. Implement ALL API endpoints defined in Section 9.
10. Implement the WebSocket endpoint for run streaming (Section 9).
11. Implement background task runner with ARQ.
12. Write tests for engine, steps, and API.

**Skills required:** Python, FastAPI, asyncio, Matrx-ORM, PostgreSQL, WebSocket.

**Critical note:** The engine MUST broadcast events through the Event Bus at every state transition. This is not optional. See Section 6.

### Track 3: Frontend Engineer

**Owns:** React + Vite app, React Flow canvas, node components, config panels, live run viewer.

**Deliverables (in order):**

1. Scaffold the Vite + React + TypeScript project with Tailwind CSS v4 (CSS-first config).
2. Initialize shadcn/ui (`pnpm dlx shadcn@latest init`) and add core components.
3. Initialize Biome for linting/formatting (`biome.json`).
4. Set up React Router with the four pages (list, builder, history, detail).
3. Set up Zustand stores for workflow state and run state.
4. Set up the API client and React Query hooks.
5. Implement the **Canvas** component with React Flow.
6. Implement the **Step Palette** (drag-and-drop).
7. Implement **BaseNode** — the shared node shell that all step nodes extend.
8. Implement ALL node components (one per step type).
9. Implement ALL config panel components (one per step type).
10. Implement the **NodeConfigPanel** container that renders the right panel per node type.
11. Implement the **WebSocket hook** (`useRunStream`).
12. Implement the **Run Overlay** — live status on canvas nodes during execution.
13. Implement the **TemplateInput** component with autocomplete for `{{context.*}}`.
14. Implement save, publish, and run controls.
15. Implement the RunHistory and RunDetail pages.

**Skills required:** React 19, TypeScript, React Flow (@xyflow/react), Tailwind CSS v4, shadcn/ui, WebSocket.

**Critical note:** The node status visualization MUST use the WebSocket event stream. Do NOT poll the API. See Section 6. All UI components MUST use shadcn/ui primitives — do not create custom buttons, inputs, selects, or dialogs from scratch.

### Coordination Points

These are moments where tracks must sync before proceeding:

| Milestone | Tracks | Gate |
|-----------|--------|------|
| Schema is migrated | Track 1 → Track 2 | Backend cannot start DB queries until schema exists |
| Event Bus is implemented | Track 2 → Track 3 | Frontend WebSocket hook depends on event format |
| API endpoints are documented | Track 2 → Track 3 | Frontend API client depends on endpoint shapes |
| Sample workflow is seeded | Track 1 → Track 3 | Frontend needs data to develop against |

---

## 5. Database Schema & Conventions

### Naming Conventions (Non-Negotiable)

- All table names: **snake_case, plural** (`workflows`, `runs`, `step_runs`)
- All column names: **snake_case** (`created_at`, `workflow_id`)
- All enum values: **snake_case** (`wait_for_approval`, `http_request`)
- Primary keys: always `id UUID DEFAULT gen_random_uuid()`
- Foreign keys: always `{table_singular}_id` (e.g., `workflow_id`, `run_id`)
- Timestamps: always `TIMESTAMPTZ`, always include `created_at`, include `updated_at` where records are mutable

### Schema

```sql
-- ============================================================
-- MIGRATION 001: Core Tables
-- ============================================================

-- Workflow definitions. Immutable once published.
CREATE TABLE workflows (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    description     TEXT DEFAULT '',
    version         INT NOT NULL DEFAULT 1,
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK (status IN ('draft', 'published', 'archived')),
    definition      JSONB NOT NULL DEFAULT '{"nodes": [], "edges": []}',
    -- definition contains the React Flow graph verbatim:
    -- {
    --   "nodes": [{"id": "...", "type": "...", "position": {...}, "data": {...}}],
    --   "edges": [{"id": "...", "source": "...", "target": "...", "data": {...}}]
    -- }
    input_schema    JSONB DEFAULT NULL,
    -- Optional JSON Schema defining expected run inputs.
    -- Used by the frontend to render an input form before starting a run.
    created_by      UUID,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE(name, version)
);

-- Execution of a workflow.
CREATE TABLE runs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id     UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    status          TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN (
                        'pending',      -- created, not yet started
                        'running',      -- engine is executing
                        'paused',       -- waiting for human/event
                        'completed',    -- all steps done
                        'failed',       -- a step failed with on_error=fail
                        'cancelled'     -- manually cancelled
                    )),
    trigger_type    TEXT NOT NULL DEFAULT 'manual'
                    CHECK (trigger_type IN ('manual', 'schedule', 'webhook', 'event')),
    input           JSONB NOT NULL DEFAULT '{}',
    context         JSONB NOT NULL DEFAULT '{}',
    -- Context accumulates outputs from all completed steps.
    -- Structure: { "input": {...}, "step_1": {...output...}, "step_2": {...output...} }
    -- The engine writes to this after each step completes.
    -- Steps read from this via {{context.step_id.field}} templates.
    error           TEXT,
    idempotency_key TEXT UNIQUE,
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Individual step execution within a run.
CREATE TABLE step_runs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id          UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    step_id         TEXT NOT NULL,
    -- step_id matches the node "id" in the workflow definition.
    -- This is NOT a foreign key — it references the JSONB graph.
    step_type       TEXT NOT NULL,
    -- Denormalized from the node definition for query convenience.
    status          TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN (
                        'pending',      -- not yet started
                        'running',      -- currently executing
                        'completed',    -- finished successfully
                        'failed',       -- threw an error
                        'skipped',      -- on the false branch of a condition
                        'waiting',      -- paused for approval/event
                        'cancelled'     -- run was cancelled while this was pending/running
                    )),
    input           JSONB DEFAULT '{}',
    -- The resolved config that was passed to the handler.
    output          JSONB DEFAULT '{}',
    -- The return value from the handler.
    error           TEXT,
    attempt         INT NOT NULL DEFAULT 1,
    -- Retry attempt number. Starts at 1.
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- A step can have multiple attempts (retries), but only ONE should be
    -- in a non-failed state at a time.
    UNIQUE(run_id, step_id, attempt)
);

-- Persistent log of all events emitted during a run.
-- This is the source of truth for run replay and audit.
CREATE TABLE run_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id          UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    step_id         TEXT,
    -- NULL for run-level events (run.started, run.completed, etc.)
    event_type      TEXT NOT NULL,
    -- Enum of all possible events. See Section 6.
    payload         JSONB NOT NULL DEFAULT '{}',
    -- Event-specific data. Always includes at minimum: { "status": "..." }
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- MIGRATION 002: Indexes
-- ============================================================

CREATE INDEX idx_runs_workflow_id ON runs(workflow_id);
CREATE INDEX idx_runs_status ON runs(status);
CREATE INDEX idx_runs_created_at ON runs(created_at DESC);
CREATE INDEX idx_runs_idempotency_key ON runs(idempotency_key) WHERE idempotency_key IS NOT NULL;

CREATE INDEX idx_step_runs_run_id ON step_runs(run_id);
CREATE INDEX idx_step_runs_status ON step_runs(status);
CREATE INDEX idx_step_runs_run_step ON step_runs(run_id, step_id);

CREATE INDEX idx_run_events_run_id ON run_events(run_id);
CREATE INDEX idx_run_events_created_at ON run_events(run_id, created_at);

CREATE INDEX idx_workflows_status ON workflows(status);
CREATE INDEX idx_workflows_name ON workflows(name);

-- ============================================================
-- MIGRATION 003: Updated_at trigger
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_workflows_updated_at
    BEFORE UPDATE ON workflows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

### Important Schema Notes

1. **Matrx-ORM Model Definitions:** The SQL schema above is the source of truth. Matrx-ORM model classes in `db/models/` MUST mirror this schema exactly. Use Matrx-ORM's reverse migration tooling to generate models from the live schema, then verify. The engine uses Matrx-ORM for all CRUD operations — raw SQL is only acceptable in Alembic migration files and complex aggregate queries that the ORM cannot express.

2. **Migration Workflow:** Alembic handles DDL schema migrations (CREATE TABLE, ALTER, indexes). Matrx-ORM handles runtime data access (queries, inserts, updates). These are complementary, not competing. When you change the schema: (a) write an Alembic migration, (b) apply it, (c) run Matrx-ORM's reverse migration to regenerate model classes, (d) verify they match.

3. **`runs.context`** is the shared scratchpad. It is the ONLY mechanism for passing data between steps. There are no "data wires" or "connectors" in the UI. Steps declare what context keys they read/write via `{{template}}` strings.

4. **`run_events`** is an append-only log. The engine writes to it. The WebSocket reads from it. The frontend consumes it. This table is the **single source of truth for what happened during a run.** It enables replay, audit, and resumability.

5. **`step_runs.input`** stores the RESOLVED config (templates already filled in). This is critical for debugging — you can see exactly what a step received, not just the template.

6. **Workflow versioning:** When a user publishes a workflow, the current draft row gets `status = 'published'`. To edit it, the frontend creates a new row with `version + 1` and `status = 'draft'`. Runs always reference a specific workflow row (which is immutable once published). This means you can always reproduce a run exactly.

---

## 6. Communication Protocol — First Class

This is the section that makes or breaks the real-time experience. The communication between the engine and the frontend is NOT an afterthought. It is a first-class system with a defined event schema, a defined transport, and defined rules for when events are emitted.

### The Event Schema

Every event has this shape:

```python
class RunEvent(BaseModel):
    id: str                     # UUID
    run_id: str                 # UUID
    step_id: str | None         # NULL for run-level events
    event_type: str             # From the enum below
    payload: dict               # Event-specific data
    created_at: datetime
```

### Event Types — Complete Enum

```python
class EventType(str, Enum):
    # ── Run-level events ──
    RUN_STARTED     = "run.started"
    RUN_COMPLETED   = "run.completed"
    RUN_FAILED      = "run.failed"
    RUN_PAUSED      = "run.paused"
    RUN_RESUMED     = "run.resumed"
    RUN_CANCELLED   = "run.cancelled"

    # ── Step-level events ──
    STEP_STARTED    = "step.started"
    STEP_COMPLETED  = "step.completed"
    STEP_FAILED     = "step.failed"
    STEP_SKIPPED    = "step.skipped"
    STEP_WAITING    = "step.waiting"     # paused for approval/event
    STEP_RETRYING   = "step.retrying"

    # ── Data events ──
    CONTEXT_UPDATED = "context.updated"  # new data added to run context
```

### Event Payloads

Each event type has a defined payload. These are **not negotiable** — the frontend depends on them.

```python
# run.started
{"status": "running"}

# run.completed
{"status": "completed", "duration_ms": 12345}

# run.failed
{"status": "failed", "error": "Step xyz failed: connection refused", "failed_step_id": "step_3"}

# run.paused
{"status": "paused", "waiting_step_id": "step_5", "reason": "Awaiting approval"}

# run.resumed
{"status": "running", "resumed_step_id": "step_5"}

# run.cancelled
{"status": "cancelled"}

# step.started
{"step_id": "step_1", "step_type": "http_request", "step_label": "Fetch User", "attempt": 1}

# step.completed
{"step_id": "step_1", "step_type": "http_request", "status": "completed",
 "output_summary": {"status_code": 200},  # truncated output for UI display
 "duration_ms": 234}

# step.failed
{"step_id": "step_1", "step_type": "http_request", "status": "failed",
 "error": "Connection refused", "attempt": 2, "will_retry": true}

# step.skipped
{"step_id": "step_4", "step_type": "send_email", "status": "skipped",
 "reason": "Condition 'step_2' evaluated to false"}

# step.waiting
{"step_id": "step_5", "step_type": "wait_for_approval", "status": "waiting",
 "waiting_for": "approval", "label": "Manager Sign-off"}

# step.retrying
{"step_id": "step_1", "attempt": 3, "max_attempts": 5,
 "backoff_seconds": 4, "error": "Timeout"}

# context.updated
{"step_id": "step_1", "keys_added": ["step_1"]}
```

### The Event Bus — In-Process

```python
# events/bus.py

import asyncio
from collections import defaultdict
from typing import Callable, Any
from datetime import datetime
import uuid

class EventBus:
    """
    In-process event bus. The engine writes events here.
    WebSocket handlers subscribe by run_id.
    Events are also persisted to run_events table.
    """

    def __init__(self, db):
        self.db = db
        self._subscribers: dict[str, list[asyncio.Queue]] = defaultdict(list)

    async def emit(self, run_id: str, event_type: str,
                   step_id: str | None = None, payload: dict | None = None):
        """
        Emit an event. This method:
        1. Persists the event to the database
        2. Pushes to all active WebSocket subscribers for this run_id
        """
        event = {
            "id": str(uuid.uuid4()),
            "run_id": run_id,
            "step_id": step_id,
            "event_type": event_type,
            "payload": payload or {},
            "created_at": datetime.utcnow().isoformat(),
        }

        # Persist
        await self.db.insert_run_event(event)

        # Broadcast to WebSocket subscribers
        for queue in self._subscribers.get(run_id, []):
            await queue.put(event)

    def subscribe(self, run_id: str) -> asyncio.Queue:
        """Subscribe to events for a run. Returns a queue to read from."""
        queue = asyncio.Queue()
        self._subscribers[run_id].append(queue)
        return queue

    def unsubscribe(self, run_id: str, queue: asyncio.Queue):
        """Unsubscribe from events for a run."""
        if run_id in self._subscribers:
            self._subscribers[run_id].remove(queue)
            if not self._subscribers[run_id]:
                del self._subscribers[run_id]
```

### When the Engine MUST Emit Events

These are mandatory emission points. The engine developer MUST call `event_bus.emit()` at each of these moments. Missing any of these breaks the frontend.

```python
# Inside WorkflowEngine.execute_run():

async def execute_run(self, run_id: str):
    # ✅ EMIT: Run started
    await self.event_bus.emit(run_id, "run.started", payload={"status": "running"})

    try:
        while True:
            # Check cancellation
            run = await self.db.get_run(run_id)
            if run["status"] == "cancelled":
                # ✅ EMIT: Run cancelled
                await self.event_bus.emit(run_id, "run.cancelled", payload={"status": "cancelled"})
                return

            ready = graph.get_ready_steps(done)
            if not ready:
                break

            results = await asyncio.gather(
                *[self._execute_step(run_id, node, context, graph) for node in ready],
                return_exceptions=True
            )

            for node, result in zip(ready, results):
                if isinstance(result, PauseExecution):
                    # ✅ EMIT: Run paused
                    await self.event_bus.emit(run_id, "run.paused", payload={
                        "status": "paused",
                        "waiting_step_id": result.step_id,
                        "reason": result.reason,
                    })
                    return  # Exit the loop — run will be resumed externally

                elif isinstance(result, Exception):
                    if node["data"].get("on_error") == "fail":
                        # ✅ EMIT: Run failed
                        await self.event_bus.emit(run_id, "run.failed", payload={
                            "status": "failed",
                            "error": str(result),
                            "failed_step_id": node["id"],
                        })
                        raise result
                else:
                    context[node["id"]] = result
                    # ✅ EMIT: Context updated
                    await self.event_bus.emit(run_id, "context.updated",
                        step_id=node["id"],
                        payload={"step_id": node["id"], "keys_added": [node["id"]]})

        # ✅ EMIT: Run completed
        await self.event_bus.emit(run_id, "run.completed", payload={
            "status": "completed",
            "duration_ms": ...,
        })

    except Exception as e:
        # ✅ EMIT: Run failed (if not already emitted)
        await self.event_bus.emit(run_id, "run.failed", payload={
            "status": "failed",
            "error": str(e),
        })


async def _execute_step(self, run_id, node, context, graph):
    # ✅ EMIT: Step started
    await self.event_bus.emit(run_id, "step.started", step_id=node["id"], payload={
        "step_id": node["id"],
        "step_type": node["type"],
        "step_label": node["data"].get("label", ""),
        "attempt": 1,
    })

    try:
        result = await handler.execute(resolved_config, context)

        # ✅ EMIT: Step completed
        await self.event_bus.emit(run_id, "step.completed", step_id=node["id"], payload={
            "step_id": node["id"],
            "step_type": node["type"],
            "status": "completed",
            "output_summary": _truncate_for_event(result),
            "duration_ms": ...,
        })
        return result

    except Exception as e:
        if will_retry:
            # ✅ EMIT: Step retrying
            await self.event_bus.emit(run_id, "step.retrying", step_id=node["id"], payload={
                "step_id": node["id"],
                "attempt": attempt,
                "max_attempts": max_attempts,
                "error": str(e),
                "backoff_seconds": backoff,
            })
        else:
            # ✅ EMIT: Step failed
            await self.event_bus.emit(run_id, "step.failed", step_id=node["id"], payload={
                "step_id": node["id"],
                "step_type": node["type"],
                "status": "failed",
                "error": str(e),
                "attempt": attempt,
            })
            raise
```

### WebSocket Endpoint

```python
# api/ws.py

@app.websocket("/ws/runs/{run_id}")
async def run_stream(websocket: WebSocket, run_id: str):
    await websocket.accept()

    queue = event_bus.subscribe(run_id)

    try:
        # First, send current state (for late joiners / reconnection)
        step_runs = await db.get_step_runs(run_id)
        await websocket.send_json({
            "type": "snapshot",
            "step_statuses": {
                sr["step_id"]: {
                    "status": sr["status"],
                    "output_summary": _truncate_for_event(sr["output"]),
                    "error": sr["error"],
                    "attempt": sr["attempt"],
                    "duration_ms": _calc_duration(sr),
                }
                for sr in step_runs
            }
        })

        # Then, stream live events
        while True:
            event = await queue.get()
            await websocket.send_json({"type": "event", **event})

    except WebSocketDisconnect:
        pass
    finally:
        event_bus.unsubscribe(run_id, queue)
```

### Frontend WebSocket Hook

```typescript
// hooks/useRunStream.ts

import { useEffect, useCallback, useRef } from 'react';
import { useRunStore } from '../stores/runStore';

export function useRunStream(runId: string | null) {
  const wsRef = useRef<WebSocket | null>(null);
  const {
    setStepStatus,
    setRunStatus,
    setSnapshot,
    setConnected,
  } = useRunStore();

  useEffect(() => {
    if (!runId) return;

    const ws = new WebSocket(`${import.meta.env.VITE_WS_URL}/ws/runs/${runId}`);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);

      if (msg.type === 'snapshot') {
        // Initial state for late joiners
        setSnapshot(msg.step_statuses);
        return;
      }

      // Live event
      const { event_type, step_id, payload } = msg;

      switch (event_type) {
        case 'step.started':
        case 'step.completed':
        case 'step.failed':
        case 'step.skipped':
        case 'step.waiting':
        case 'step.retrying':
          setStepStatus(step_id, payload);
          break;

        case 'run.started':
        case 'run.completed':
        case 'run.failed':
        case 'run.paused':
        case 'run.resumed':
        case 'run.cancelled':
          setRunStatus(payload);
          break;
      }
    };

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [runId]);

  return wsRef;
}
```

### The Golden Rule of Communication

> **Every state transition in the engine has exactly one event. Every event has exactly one handler in the frontend. No exceptions.**

If a step starts, there is a `step.started` event. If the frontend needs to show a spinner on a node, it listens for `step.started`. There is no "check if the step is probably running" logic. There is no polling. There is no inference. **Events are facts. The UI renders facts.**

---

## 7. Python Backend — Execution Engine

### The Graph Helper

```python
# engine/graph.py

from collections import defaultdict

class Graph:
    """
    Lightweight DAG helper built from React Flow nodes and edges.
    This class is pure logic — no I/O, no database, no side effects.
    """

    def __init__(self, nodes: list[dict], edges: list[dict]):
        self.nodes: dict[str, dict] = {n["id"]: n for n in nodes}
        self.edges: list[dict] = edges

        # Build adjacency structures
        self.dependencies: dict[str, set[str]] = defaultdict(set)
        self.children: dict[str, list[tuple[str, dict]]] = defaultdict(list)

        for edge in edges:
            self.dependencies[edge["target"]].add(edge["source"])
            self.children[edge["source"]].append(
                (edge["target"], edge.get("data", {}))
            )

        # Root nodes have no incoming edges
        all_targets = {e["target"] for e in edges}
        self.root_ids = set(self.nodes.keys()) - all_targets

    def get_ready_steps(self, done_ids: set[str]) -> list[dict]:
        """
        Return all nodes whose dependencies are fully satisfied
        and that haven't been processed yet.

        This is the ENTIRE scheduling algorithm.
        """
        ready = []
        for node_id, node in self.nodes.items():
            if node_id in done_ids:
                continue
            deps = self.dependencies.get(node_id, set())
            if deps.issubset(done_ids):
                ready.append(node)
        return ready

    def get_branch_nodes(self, condition_id: str, branch_label: str) -> set[str]:
        """
        Get all downstream node IDs on a specific branch of a condition.
        Used to mark the 'false' branch as skipped.
        """
        targets = set()
        for target_id, edge_data in self.children.get(condition_id, []):
            if edge_data.get("condition") == branch_label:
                targets |= self._all_descendants(target_id)
        return targets

    def _all_descendants(self, node_id: str) -> set[str]:
        """Recursively collect all nodes downstream of node_id."""
        result = {node_id}
        for child_id, _ in self.children.get(node_id, []):
            result |= self._all_descendants(child_id)
        return result

    def get_upstream_ids(self, node_id: str) -> set[str]:
        """Get all ancestor node IDs (for template reference validation)."""
        result = set()
        for dep_id in self.dependencies.get(node_id, set()):
            result.add(dep_id)
            result |= self.get_upstream_ids(dep_id)
        return result
```

### Template Resolution

```python
# engine/templates.py

import re
from typing import Any
from jinja2 import Environment, BaseLoader, StrictUndefined

# Use Jinja2 for complex templates, regex for simple {{var}} references
_simple_pattern = re.compile(r"\{\{(.+?)\}\}")

_jinja_env = Environment(
    loader=BaseLoader(),
    undefined=StrictUndefined,  # Raise error on missing keys — don't silently produce empty string
    variable_start_string="{{",
    variable_end_string="}}",
)


def resolve_templates(obj: Any, scope: dict) -> Any:
    """
    Recursively resolve {{template}} strings in any data structure.

    `scope` is the full context dict:
    {
        "input": { ... run input ... },
        "step_1": { ... step 1 output ... },
        "step_2": { ... step 2 output ... },
    }

    Template examples:
        "{{input.user_id}}"                    → simple variable lookup
        "Hello {{step_1.name}}"                → string interpolation
        "{{step_1.items | length}}"            → Jinja2 filter
        "{% for item in step_1.items %}..."    → Jinja2 loop (for complex transforms)
    """
    if isinstance(obj, str):
        # Check if the entire string is one template (preserve type)
        match = _simple_pattern.fullmatch(obj.strip())
        if match:
            # Return the actual value (could be dict, list, int, etc.)
            return _deep_get(scope, match.group(1).strip())

        # Otherwise, render as Jinja2 string template
        if "{{" in obj or "{%" in obj:
            template = _jinja_env.from_string(obj)
            return template.render(**scope)

        return obj

    if isinstance(obj, dict):
        return {k: resolve_templates(v, scope) for k, v in obj.items()}

    if isinstance(obj, list):
        return [resolve_templates(item, scope) for item in obj]

    return obj


def _deep_get(data: dict, path: str) -> Any:
    """Navigate nested dicts/lists by dot path. e.g., 'step_1.users.0.name'"""
    keys = path.split(".")
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current[key]
        elif isinstance(current, list):
            current = current[int(key)]
        else:
            raise KeyError(f"Cannot traverse into {type(current)} with key '{key}'")
    return current


def extract_template_refs(obj: Any) -> set[str]:
    """
    Extract all {{context.*}} references from a config.
    Used for validation — ensuring all references point to upstream steps.
    """
    refs = set()
    if isinstance(obj, str):
        for match in _simple_pattern.finditer(obj):
            refs.add(match.group(1).strip())
    elif isinstance(obj, dict):
        for v in obj.values():
            refs |= extract_template_refs(v)
    elif isinstance(obj, list):
        for item in obj:
            refs |= extract_template_refs(item)
    return refs
```

### Workflow Validation

```python
# validation/workflow.py

from engine.graph import Graph
from engine.templates import extract_template_refs

def validate_workflow(definition: dict) -> list[str]:
    """
    Validate a workflow definition before publishing or running.
    Returns a list of error messages. Empty list = valid.
    """
    errors = []
    nodes = definition.get("nodes", [])
    edges = definition.get("edges", [])
    node_map = {n["id"]: n for n in nodes}
    node_ids = set(node_map.keys())

    # 1. Must have at least one node
    if not nodes:
        errors.append("Workflow must have at least one step.")
        return errors

    # 2. All edge endpoints must reference existing nodes
    for edge in edges:
        if edge["source"] not in node_ids:
            errors.append(f"Edge '{edge['id']}' references non-existent source node: '{edge['source']}'")
        if edge["target"] not in node_ids:
            errors.append(f"Edge '{edge['id']}' references non-existent target node: '{edge['target']}'")

    if errors:
        return errors  # Can't build graph with bad edges

    # 3. Cycle detection (workflow must be a DAG)
    if _has_cycle(node_ids, edges):
        errors.append("Workflow contains a cycle. Workflows must be directed acyclic graphs (DAGs).")

    # 4. All node types must be registered
    from steps.registry import STEP_REGISTRY
    for node in nodes:
        if node["type"] not in STEP_REGISTRY and node["type"] not in ("condition", "wait_for_approval"):
            errors.append(f"Node '{node['id']}' has unregistered step type: '{node['type']}'")

    # 5. Condition nodes must have exactly one 'true' and one 'false' outgoing edge
    for node in nodes:
        if node["type"] == "condition":
            outgoing = [e for e in edges if e["source"] == node["id"]]
            labels = sorted([e.get("data", {}).get("condition", "MISSING") for e in outgoing])
            if labels != ["false", "true"]:
                errors.append(
                    f"Condition node '{node['id']}' must have exactly two outgoing edges "
                    f"labeled 'true' and 'false'. Found: {labels}"
                )

    # 6. No orphan nodes in multi-node workflows
    if len(nodes) > 1:
        connected = set()
        for edge in edges:
            connected.add(edge["source"])
            connected.add(edge["target"])
        orphans = node_ids - connected
        if orphans:
            errors.append(f"Disconnected nodes found: {orphans}. All nodes must be connected.")

    # 7. Template references must point to upstream steps
    graph = Graph(nodes, edges)
    for node in nodes:
        config = node.get("data", {}).get("config", {})
        refs = extract_template_refs(config)
        upstream = graph.get_upstream_ids(node["id"])

        for ref in refs:
            parts = ref.split(".")
            root = parts[0]
            if root == "input":
                continue  # Always valid — refers to run input
            if root not in upstream:
                errors.append(
                    f"Node '{node['id']}' references '{{{{{{{{ref}}}}}}}}' but "
                    f"'{root}' is not an upstream dependency. "
                    f"Data can only flow from upstream to downstream steps."
                )

    return errors


def _has_cycle(node_ids: set[str], edges: list[dict]) -> bool:
    """Topological sort-based cycle detection."""
    from collections import defaultdict, deque

    in_degree = {nid: 0 for nid in node_ids}
    adj = defaultdict(list)

    for edge in edges:
        adj[edge["source"]].append(edge["target"])
        in_degree[edge["target"]] += 1

    queue = deque([nid for nid, deg in in_degree.items() if deg == 0])
    visited = 0

    while queue:
        node = queue.popleft()
        visited += 1
        for child in adj[node]:
            in_degree[child] -= 1
            if in_degree[child] == 0:
                queue.append(child)

    return visited != len(node_ids)
```

### The Execution Engine

```python
# engine/executor.py

import asyncio
import time
from datetime import datetime, timezone
from typing import Any

from .graph import Graph
from .templates import resolve_templates
from .exceptions import PauseExecution, StepTimeout
from events.bus import EventBus


class WorkflowEngine:

    def __init__(self, db, event_bus: EventBus, step_registry: dict):
        self.db = db
        self.event_bus = event_bus
        self.registry = step_registry
        self._active_tasks: dict[str, set[asyncio.Task]] = {}

    async def execute_run(self, run_id: str):
        """
        Main execution loop.

        Algorithm:
        1. Build graph from workflow definition
        2. Find all steps with satisfied dependencies ("ready")
        3. Execute them in parallel with asyncio.gather
        4. Update context with outputs
        5. Repeat until no more ready steps, or failure/pause

        This loop is IDEMPOTENT. Calling it on a partially-completed run
        will pick up where it left off (it queries the DB for done steps).
        """
        run = await self.db.get_run(run_id)
        workflow = await self.db.get_workflow(run["workflow_id"])
        definition = workflow["definition"]

        graph = Graph(definition["nodes"], definition["edges"])
        context = dict(run.get("context", {}))
        context["input"] = run.get("input", {})

        # Update run status
        await self.db.update_run(run_id, status="running", started_at=datetime.now(timezone.utc))
        await self.event_bus.emit(run_id, "run.started", payload={"status": "running"})

        run_start = time.monotonic()
        self._active_tasks[run_id] = set()

        try:
            while True:
                # ── Check for cancellation ──
                run = await self.db.get_run(run_id)
                if run["status"] == "cancelled":
                    await self.event_bus.emit(run_id, "run.cancelled",
                        payload={"status": "cancelled"})
                    return

                # ── Find ready steps ──
                completed_ids = await self.db.get_step_ids_by_status(run_id, ("completed",))
                skipped_ids = await self.db.get_step_ids_by_status(run_id, ("skipped",))
                done_ids = completed_ids | skipped_ids

                ready_nodes = graph.get_ready_steps(done_ids)

                if not ready_nodes:
                    break  # All steps processed

                # ── Execute ready steps in parallel ──
                tasks = []
                for node in ready_nodes:
                    task = asyncio.create_task(
                        self._execute_step(run_id, node, context, graph)
                    )
                    tasks.append((node, task))
                    self._active_tasks[run_id].add(task)

                # Wait for all parallel steps to complete
                results = await asyncio.gather(
                    *[t for _, t in tasks],
                    return_exceptions=True
                )

                # ── Process results ──
                for (node, task), result in zip(tasks, results):
                    self._active_tasks[run_id].discard(task)

                    if isinstance(result, PauseExecution):
                        # Run is paused — exit the loop
                        await self.db.update_run(run_id, status="paused", context=context)
                        await self.event_bus.emit(run_id, "run.paused", payload={
                            "status": "paused",
                            "waiting_step_id": result.step_id,
                            "reason": result.reason,
                        })
                        return  # Will be resumed by external API call

                    elif isinstance(result, Exception):
                        on_error = node["data"].get("on_error", "fail")

                        if on_error == "skip":
                            await self.db.create_step_run(
                                run_id=run_id, step_id=node["id"],
                                step_type=node["type"], status="skipped"
                            )
                            await self.event_bus.emit(run_id, "step.skipped",
                                step_id=node["id"], payload={
                                    "step_id": node["id"],
                                    "status": "skipped",
                                    "reason": f"Error skipped: {str(result)}",
                                })
                            continue

                        # on_error == "fail" (default)
                        await self.db.update_run(
                            run_id, status="failed", error=str(result),
                            context=context, completed_at=datetime.now(timezone.utc)
                        )
                        await self.event_bus.emit(run_id, "run.failed", payload={
                            "status": "failed",
                            "error": str(result),
                            "failed_step_id": node["id"],
                        })
                        return

                    else:
                        # Success — update context
                        context[node["id"]] = result
                        await self.db.update_run(run_id, context=context)
                        await self.event_bus.emit(run_id, "context.updated",
                            step_id=node["id"],
                            payload={"step_id": node["id"], "keys_added": [node["id"]]})

            # ── All done ──
            duration_ms = round((time.monotonic() - run_start) * 1000)
            await self.db.update_run(
                run_id, status="completed", context=context,
                completed_at=datetime.now(timezone.utc)
            )
            await self.event_bus.emit(run_id, "run.completed", payload={
                "status": "completed",
                "duration_ms": duration_ms,
            })

        except Exception as e:
            await self.db.update_run(
                run_id, status="failed", error=str(e),
                context=context, completed_at=datetime.now(timezone.utc)
            )
            await self.event_bus.emit(run_id, "run.failed", payload={
                "status": "failed",
                "error": str(e),
            })

        finally:
            # Cancel any remaining tasks
            for task in self._active_tasks.pop(run_id, set()):
                task.cancel()


    async def _execute_step(self, run_id: str, node: dict,
                             context: dict, graph: Graph) -> Any:
        step_id = node["id"]
        step_type = node["type"]
        config = node.get("data", {}).get("config", {})
        retry_config = node["data"].get("retry", {"max_attempts": 1, "backoff": "fixed"})
        timeout_seconds = node["data"].get("timeout_seconds", 300)
        max_attempts = retry_config.get("max_attempts", 1)

        # ── Handle condition nodes ──
        if step_type == "condition":
            return await self._evaluate_condition(run_id, node, context, graph)

        # ── Handle approval/wait nodes ──
        if step_type == "wait_for_approval":
            await self.event_bus.emit(run_id, "step.waiting", step_id=step_id, payload={
                "step_id": step_id,
                "step_type": step_type,
                "status": "waiting",
                "waiting_for": "approval",
                "label": node["data"].get("label", "Approval Required"),
            })
            await self.db.create_step_run(
                run_id=run_id, step_id=step_id,
                step_type=step_type, status="waiting"
            )
            raise PauseExecution(step_id=step_id, reason="Awaiting approval")

        # ── Resolve templates ──
        resolved_config = resolve_templates(config, context)

        # ── Get handler ──
        handler = self.registry.get(step_type)
        if not handler:
            raise ValueError(f"No handler registered for step type: {step_type}")

        # ── Execute with retry ──
        last_error = None

        for attempt in range(1, max_attempts + 1):
            step_start = time.monotonic()

            # Create step_run record
            step_run_id = await self.db.create_step_run(
                run_id=run_id, step_id=step_id, step_type=step_type,
                status="running", input=resolved_config, attempt=attempt,
                started_at=datetime.now(timezone.utc)
            )

            # Emit step started
            await self.event_bus.emit(run_id, "step.started", step_id=step_id, payload={
                "step_id": step_id,
                "step_type": step_type,
                "step_label": node["data"].get("label", ""),
                "attempt": attempt,
            })

            try:
                result = await asyncio.wait_for(
                    handler.execute(resolved_config, context),
                    timeout=timeout_seconds
                )

                duration_ms = round((time.monotonic() - step_start) * 1000)

                # Validate output size
                result = handler.validate_output(result)

                # Save to database
                await self.db.update_step_run(
                    step_run_id, status="completed", output=result,
                    completed_at=datetime.now(timezone.utc)
                )

                # Emit step completed
                await self.event_bus.emit(run_id, "step.completed", step_id=step_id, payload={
                    "step_id": step_id,
                    "step_type": step_type,
                    "status": "completed",
                    "output_summary": _truncate_for_display(result),
                    "duration_ms": duration_ms,
                })

                return result

            except asyncio.TimeoutError:
                last_error = StepTimeout(f"Step '{step_id}' timed out after {timeout_seconds}s")
            except PauseExecution:
                raise  # Don't catch pause — let it propagate
            except Exception as e:
                last_error = e

            # ── Handle failure / retry ──
            duration_ms = round((time.monotonic() - step_start) * 1000)
            will_retry = attempt < max_attempts

            await self.db.update_step_run(
                step_run_id, status="failed", error=str(last_error),
                completed_at=datetime.now(timezone.utc)
            )

            if will_retry:
                backoff_seconds = _calculate_backoff(attempt, retry_config)
                await self.event_bus.emit(run_id, "step.retrying", step_id=step_id, payload={
                    "step_id": step_id,
                    "attempt": attempt,
                    "max_attempts": max_attempts,
                    "backoff_seconds": backoff_seconds,
                    "error": str(last_error),
                })
                await asyncio.sleep(backoff_seconds)
            else:
                await self.event_bus.emit(run_id, "step.failed", step_id=step_id, payload={
                    "step_id": step_id,
                    "step_type": step_type,
                    "status": "failed",
                    "error": str(last_error),
                    "attempt": attempt,
                })
                raise last_error


    async def _evaluate_condition(self, run_id: str, node: dict,
                                   context: dict, graph: Graph) -> dict:
        step_id = node["id"]
        expression = resolve_templates(
            node["data"]["config"]["expression"], context
        )

        # Emit started
        await self.event_bus.emit(run_id, "step.started", step_id=step_id, payload={
            "step_id": step_id,
            "step_type": "condition",
            "step_label": node["data"].get("label", ""),
            "attempt": 1,
        })

        result = safe_eval(expression)
        result_bool = bool(result)

        # Save condition result
        await self.db.create_step_run(
            run_id=run_id, step_id=step_id, step_type="condition",
            status="completed", output={"result": result_bool},
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc)
        )

        await self.event_bus.emit(run_id, "step.completed", step_id=step_id, payload={
            "step_id": step_id,
            "step_type": "condition",
            "status": "completed",
            "output_summary": {"result": result_bool},
            "duration_ms": 0,
        })

        # Skip the losing branch
        losing_branch = "false" if result_bool else "true"
        skip_ids = graph.get_branch_nodes(step_id, losing_branch)

        for skip_id in skip_ids:
            skip_node = graph.nodes.get(skip_id, {})
            await self.db.create_step_run(
                run_id=run_id, step_id=skip_id,
                step_type=skip_node.get("type", "unknown"),
                status="skipped"
            )
            await self.event_bus.emit(run_id, "step.skipped", step_id=skip_id, payload={
                "step_id": skip_id,
                "status": "skipped",
                "reason": f"Condition '{step_id}' evaluated to {result_bool}",
            })

        return {"result": result_bool}


def _calculate_backoff(attempt: int, config: dict) -> float:
    strategy = config.get("backoff", "fixed")
    base = config.get("backoff_base", 2)

    if strategy == "exponential":
        return base ** attempt
    elif strategy == "linear":
        return base * attempt
    else:  # fixed
        return base


def _truncate_for_display(output: Any, max_keys: int = 5) -> dict:
    """Create a small summary of step output for WebSocket events."""
    if not isinstance(output, dict):
        return {"value": str(output)[:200]}

    summary = {}
    for i, (k, v) in enumerate(output.items()):
        if i >= max_keys:
            summary["_more"] = f"...and {len(output) - max_keys} more keys"
            break
        if isinstance(v, str) and len(v) > 200:
            summary[k] = v[:200] + "..."
        elif isinstance(v, (list, dict)):
            summary[k] = f"({type(v).__name__}, {len(v)} items)"
        else:
            summary[k] = v

    return summary
```

---

## 8. Step Handler System — The Plugin Architecture

### The Base Class

```python
# steps/base.py

from abc import ABC, abstractmethod
from typing import Any
import json

class StepHandler(ABC):
    """
    Base class for all step handlers.

    Contract:
    - execute() receives resolved config (templates already filled) and full context
    - execute() returns JSON-serializable output (gets stored in run context)
    - execute() raises Exception on failure (engine handles retries)

    That's the entire contract. Everything else is engine-level config.
    """

    MAX_OUTPUT_SIZE: int = 100_000  # 100KB default
    CONTEXT_FIELDS: set[str] = set()  # Override to specify which fields to keep when truncating

    @abstractmethod
    async def execute(self, config: dict, context: dict) -> Any:
        """Execute the step. Returns JSON-serializable output."""
        ...

    def validate_output(self, output: Any) -> Any:
        """Ensure output isn't too large for the context dict."""
        try:
            serialized = json.dumps(output)
        except (TypeError, ValueError):
            return {"_error": "Output not JSON-serializable", "value": str(output)[:1000]}

        if len(serialized) > self.MAX_OUTPUT_SIZE:
            if isinstance(output, dict) and self.CONTEXT_FIELDS:
                return {
                    "_truncated": True,
                    "_original_size": len(serialized),
                    **{k: v for k, v in output.items() if k in self.CONTEXT_FIELDS}
                }
            return {
                "_truncated": True,
                "_original_size": len(serialized),
                "_preview": str(output)[:500],
            }

        return output
```

### Step Handler Implementations

```python
# steps/http_request.py
import httpx

class HttpRequestHandler(StepHandler):
    CONTEXT_FIELDS = {"status_code", "body"}

    async def execute(self, config: dict, context: dict) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.request(
                method=config["method"],
                url=config["url"],
                headers=config.get("headers", {}),
                json=config.get("body") if config.get("body") else None,
                params=config.get("params"),
            )
            response.raise_for_status()

            # Try to parse JSON, fall back to text
            try:
                body = response.json()
            except Exception:
                body = response.text

            return {
                "status_code": response.status_code,
                "body": body,
                "headers": dict(response.headers),
            }


# steps/llm_call.py
class LLMCallHandler(StepHandler):
    """
    Calls AI Matrx's LLM integration packages.
    Supports: anthropic, openai, google.
    """
    CONTEXT_FIELDS = {"content", "model", "usage"}

    async def execute(self, config: dict, context: dict) -> dict:
        provider = config.get("provider", "anthropic")
        model = config["model"]
        messages = config.get("messages", [{"role": "user", "content": config["prompt"]}])
        system = config.get("system_prompt")
        max_tokens = config.get("max_tokens", 1024)
        temperature = config.get("temperature", 0.7)

        # Use AI Matrx's LLM packages directly
        # These are imported from your existing packages
        if provider == "anthropic":
            from aimatrx_llm.anthropic import call_anthropic
            response = await call_anthropic(
                model=model, messages=messages, system=system,
                max_tokens=max_tokens, temperature=temperature
            )
        elif provider == "openai":
            from aimatrx_llm.openai import call_openai
            response = await call_openai(
                model=model, messages=messages, system=system,
                max_tokens=max_tokens, temperature=temperature
            )
        elif provider == "google":
            from aimatrx_llm.google import call_google
            response = await call_google(
                model=model, messages=messages, system=system,
                max_tokens=max_tokens, temperature=temperature
            )
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")

        return {
            "content": response["content"],
            "model": response.get("model", model),
            "usage": response.get("usage", {}),
            "provider": provider,
        }


# steps/inline_code.py
import json as json_module

class InlineCodeHandler(StepHandler):
    """
    Execute sandboxed Python code with access to context.
    The code MUST set `result` to its output value.
    """

    SAFE_BUILTINS = {
        # Types
        "int": int, "float": float, "str": str, "bool": bool,
        "list": list, "dict": dict, "set": set, "tuple": tuple,
        "type": type, "isinstance": isinstance,
        # Constants
        "None": None, "True": True, "False": False,
        # Iterables
        "range": range, "len": len, "sorted": sorted,
        "min": min, "max": max, "sum": sum,
        "any": any, "all": all,
        "zip": zip, "enumerate": enumerate, "map": map, "filter": filter,
        "reversed": reversed,
        # String
        "ord": ord, "chr": chr,
        # Math
        "abs": abs, "round": round, "pow": pow,
        # JSON
        "json_dumps": json_module.dumps,
        "json_loads": json_module.loads,
        # Printing (captured, not actually printed)
        "print": lambda *args: None,
    }

    async def execute(self, config: dict, context: dict) -> dict:
        code = config["code"]
        local_vars = {
            "context": context,
            "input": context.get("input", {}),
            "result": None,
        }

        exec(code, {"__builtins__": self.SAFE_BUILTINS}, local_vars)

        if local_vars["result"] is None:
            raise ValueError(
                "Inline code must set 'result'. "
                "Example: result = context['step_1']['items'][:5]"
            )

        return {"result": local_vars["result"]}


# steps/database_query.py
class DatabaseQueryHandler(StepHandler):
    """
    Executes user-defined SQL queries configured in the workflow step.
    This is one of the acceptable cases for raw SQL (per Schema Notes #1)
    because the query is authored by the workflow creator, not hardcoded.
    Uses the Matrx-ORM connection pool under the hood.
    """
    async def execute(self, config: dict, context: dict) -> dict:
        query = config["query"]
        params = config.get("params", [])
        # Uses Matrx-ORM's underlying asyncpg connection pool
        rows = await self.db.fetch(query, *params)
        return {
            "rows": [dict(row) for row in rows],
            "count": len(rows),
        }


# steps/delay.py
import asyncio

class DelayHandler(StepHandler):
    async def execute(self, config: dict, context: dict) -> dict:
        seconds = config.get("seconds", 0)
        await asyncio.sleep(seconds)
        return {"delayed_seconds": seconds}


# steps/transform.py
class TransformHandler(StepHandler):
    """
    Simple data transformation using Jinja2 templates.
    Outputs a structured object based on a template.
    """
    async def execute(self, config: dict, context: dict) -> dict:
        # Config is already template-resolved, so the output IS the result
        return config.get("output", {})


# steps/send_email.py
class SendEmailHandler(StepHandler):
    async def execute(self, config: dict, context: dict) -> dict:
        # Use AI Matrx's email service
        from aimatrx_email import send_email
        result = await send_email(
            to=config["to"],
            subject=config["subject"],
            body=config["body"],
            html=config.get("html", False),
        )
        return {"sent": True, "message_id": result.get("message_id")}


# steps/webhook.py
import httpx

class WebhookHandler(StepHandler):
    async def execute(self, config: dict, context: dict) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                config["url"],
                json=config.get("payload", {}),
                headers=config.get("headers", {}),
            )
            return {
                "status_code": response.status_code,
                "body": response.text[:1000],
            }
```

### The Registry

```python
# steps/registry.py

from .http_request import HttpRequestHandler
from .llm_call import LLMCallHandler
from .inline_code import InlineCodeHandler
from .database_query import DatabaseQueryHandler
from .delay import DelayHandler
from .transform import TransformHandler
from .send_email import SendEmailHandler
from .webhook import WebhookHandler

# This dict IS the plugin system.
# To add a new step type:
# 1. Write a handler class (one file, one class, one execute method)
# 2. Add it here (one line)
# 3. Add a React node component + config panel in the frontend

STEP_REGISTRY: dict[str, StepHandler] = {
    "http_request":     HttpRequestHandler(),
    "llm_call":         LLMCallHandler(),
    "inline_code":      InlineCodeHandler(),
    "database_query":   DatabaseQueryHandler(),
    "delay":            DelayHandler(),
    "transform":        TransformHandler(),
    "send_email":       SendEmailHandler(),
    "webhook":          WebhookHandler(),
    # Handled by the engine directly (no handler class):
    # "condition"
    # "wait_for_approval"
    # "wait_for_event"
}

# Step metadata for the frontend palette
STEP_CATALOG = [
    {"type": "http_request",    "label": "HTTP Request",    "icon": "globe",     "category": "integrations", "description": "Make HTTP API calls"},
    {"type": "llm_call",        "label": "LLM Call",        "icon": "brain",     "category": "ai",           "description": "Call AI models (Anthropic, OpenAI, Google)"},
    {"type": "inline_code",     "label": "Code",            "icon": "code",      "category": "logic",        "description": "Run custom Python code"},
    {"type": "condition",       "label": "Condition",       "icon": "git-branch","category": "logic",        "description": "Branch based on a condition"},
    {"type": "database_query",  "label": "Database Query",  "icon": "database",  "category": "data",         "description": "Query PostgreSQL"},
    {"type": "transform",       "label": "Transform",       "icon": "shuffle",   "category": "data",         "description": "Reshape data between steps"},
    {"type": "delay",           "label": "Delay",           "icon": "clock",     "category": "flow",         "description": "Wait for a specified duration"},
    {"type": "wait_for_approval","label": "Approval",       "icon": "user-check","category": "flow",         "description": "Pause and wait for human approval"},
    {"type": "send_email",      "label": "Send Email",      "icon": "mail",      "category": "integrations", "description": "Send an email"},
    {"type": "webhook",         "label": "Webhook",         "icon": "webhook",   "category": "integrations", "description": "Call an external webhook"},
]
```

---

## 9. API Layer

### Complete Endpoint Specification

```python
# api/router.py

from fastapi import APIRouter
from .workflows import router as workflows_router
from .runs import router as runs_router
from .triggers import router as triggers_router
from .catalog import router as catalog_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(workflows_router, prefix="/workflows", tags=["workflows"])
api_router.include_router(runs_router, prefix="/runs", tags=["runs"])
api_router.include_router(triggers_router, prefix="/triggers", tags=["triggers"])
api_router.include_router(catalog_router, prefix="/catalog", tags=["catalog"])
```

### Workflow Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/workflows` | List all workflows (with pagination, filtering by status) |
| POST | `/api/v1/workflows` | Create a new workflow |
| GET | `/api/v1/workflows/{id}` | Get a single workflow (returns definition for React Flow) |
| PUT | `/api/v1/workflows/{id}` | Update a draft workflow (saves the React Flow graph) |
| DELETE | `/api/v1/workflows/{id}` | Delete a draft workflow (cannot delete published) |
| POST | `/api/v1/workflows/{id}/publish` | Publish a workflow (freeze definition, make runnable) |
| POST | `/api/v1/workflows/{id}/validate` | Validate a workflow definition (returns errors) |
| POST | `/api/v1/workflows/{id}/duplicate` | Create a copy as a new draft |

### Run Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/workflows/{id}/run` | Start a new run (returns run object with ID) |
| GET | `/api/v1/runs` | List runs (filter by workflow_id, status, date range) |
| GET | `/api/v1/runs/{id}` | Get run details (status, context, timing) |
| GET | `/api/v1/runs/{id}/steps` | Get all step_runs for a run |
| GET | `/api/v1/runs/{id}/events` | Get all events for a run (for replay) |
| POST | `/api/v1/runs/{id}/resume` | Resume a paused run (with approval data) |
| POST | `/api/v1/runs/{id}/cancel` | Cancel a running/paused run |
| POST | `/api/v1/runs/{id}/retry` | Retry a failed run from the failed step |

### WebSocket Endpoint

| Protocol | Path | Purpose |
|----------|------|---------|
| WS | `/ws/runs/{id}` | Stream live events for a run |

### Catalog Endpoint

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/catalog/steps` | Returns STEP_CATALOG (step types + metadata for the palette) |

### Request/Response Models

```python
# db/models.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any

# ── Workflows ──

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

# ── Runs ──

class RunInput(BaseModel):
    input: dict = Field(default_factory=dict)
    idempotency_key: str | None = None

class ResumeInput(BaseModel):
    step_id: str
    data: dict = Field(default_factory=dict)  # approval data, event data, etc.

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

# ── Validation ──

class ValidationResponse(BaseModel):
    valid: bool
    errors: list[str]
```

### Idempotency (Non-Negotiable)

Every endpoint that creates a resource MUST support an idempotency key via the `X-Idempotency-Key` header. The run trigger endpoint MUST check for existing runs with the same key before creating a new one. This prevents duplicate runs from webhook retries, network issues, or double-clicks.

### CORS Configuration

```python
# main.py

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        # Add production frontend URL here
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 10. Frontend — React + Vite + React Flow

### Project Initialization

```bash
# Scaffold with Vite
pnpm create vite frontend --template react-ts
cd frontend

# Core dependencies
pnpm add @xyflow/react zustand @tanstack/react-query react-router @monaco-editor/react dagre lucide-react
pnpm add react-hook-form zod @hookform/resolvers
pnpm add sonner date-fns motion clsx tailwind-merge
pnpm add -D tailwindcss @tailwindcss/vite @types/dagre

# Initialize shadcn/ui (interactive — choose "New York" style, CSS variables)
pnpm dlx shadcn@latest init

# Add common shadcn components
pnpm dlx shadcn@latest add button input select dialog dropdown-menu tooltip badge separator

# Initialize Biome (replaces ESLint + Prettier)
pnpm add -D @biomejs/biome
pnpm dlx @biomejs/biome init
```

### Tailwind v4 CSS Entry Point

There is NO `tailwind.config.js` or `tailwind.config.ts`. All configuration lives in CSS:

```css
/* src/index.css */
@import "tailwindcss";

@theme {
  --color-brand-50: #f0f9ff;
  --color-brand-500: #3b82f6;
  --color-brand-600: #2563eb;
  --font-sans: "Inter", system-ui, sans-serif;
}
```

### The `cn()` Utility

This is generated by shadcn/ui init and used in every component that accepts `className`:

```typescript
// lib/utils.ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

### The Zod + React Hook Form Pattern

All config panels use this pattern. Define the schema once, derive the type, use in the form:

```typescript
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

const httpRequestSchema = z.object({
  method: z.enum(["GET", "POST", "PUT", "PATCH", "DELETE"]),
  url: z.string().min(1, "URL is required"),
  headers: z.record(z.string()).optional(),
  body: z.string().optional(),
});

type HttpRequestConfig = z.infer<typeof httpRequestSchema>;

function HttpRequestConfigPanel({ config, onChange }: ConfigPanelProps) {
  const form = useForm<HttpRequestConfig>({
    resolver: zodResolver(httpRequestSchema),
    defaultValues: config,
  });
  // ...
}
```

### The Canvas — Core Component

```tsx
// pages/WorkflowBuilder.tsx

import { ReactFlow, Background, Controls, MiniMap, Panel,
         useNodesState, useEdgesState, addEdge,
         type Connection, type Node, type Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { nodeTypes } from '../nodes';
import { StepPalette } from '../components/canvas/StepPalette';
import { NodeConfigPanel } from '../components/canvas/NodeConfigPanel';
import { RunControls } from '../components/run/RunControls';
import { RunOverlay } from '../components/run/RunOverlay';
import { useWorkflow } from '../hooks/useWorkflow';
import { useRunStream } from '../hooks/useRunStream';
import { useRunStore } from '../stores/runStore';

export function WorkflowBuilder({ workflowId }: { workflowId: string }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  const { workflow, save, publish, isLoading } = useWorkflow(workflowId);
  const { activeRunId } = useRunStore();
  useRunStream(activeRunId);

  // Load definition into React Flow
  useEffect(() => {
    if (workflow?.definition) {
      setNodes(workflow.definition.nodes);
      setEdges(workflow.definition.edges);
    }
  }, [workflow]);

  // Save = serialize React Flow state
  const handleSave = async () => {
    await save({ definition: { nodes, edges } });
  };

  // Node selection
  const onNodeClick = (_: any, node: Node) => setSelectedNode(node);
  const onPaneClick = () => setSelectedNode(null);

  // Config change from panel
  const onConfigChange = (nodeId: string, newData: any) => {
    setNodes(nds => nds.map(n =>
      n.id === nodeId ? { ...n, data: { ...n.data, ...newData } } : n
    ));
  };

  return (
    <div className="h-screen w-full flex">
      {/* Left: Step palette */}
      <StepPalette />

      {/* Center: Canvas */}
      <div className="flex-1 relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={(conn: Connection) => setEdges(eds => addEdge(conn, eds))}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
          nodeTypes={nodeTypes}
          fitView
          snapToGrid
          snapGrid={[16, 16]}
        >
          <Background gap={16} size={1} />
          <Controls />
          <MiniMap />
          <Panel position="top-right">
            <RunControls
              workflowId={workflowId}
              onSave={handleSave}
              onPublish={publish}
            />
          </Panel>
        </ReactFlow>

        {/* Live run status overlay */}
        {activeRunId && <RunOverlay />}
      </div>

      {/* Right: Config panel */}
      {selectedNode && (
        <NodeConfigPanel
          node={selectedNode}
          onChange={(data) => onConfigChange(selectedNode.id, data)}
          upstreamStepIds={getUpstreamIds(selectedNode.id, edges)}
        />
      )}
    </div>
  );
}
```

### The BaseNode Pattern

Every custom node MUST extend this pattern. No exceptions.

```tsx
// nodes/BaseNode.tsx

import { Handle, Position, type NodeProps } from '@xyflow/react';
import { useRunStore } from '../stores/runStore';
import { cn } from '../lib/utils';

interface BaseNodeProps extends NodeProps {
  icon: React.ReactNode;
  children?: React.ReactNode;
}

const STATUS_STYLES = {
  pending:   'border-gray-200 bg-white',
  running:   'border-blue-400 bg-blue-50 ring-2 ring-blue-200 animate-pulse',
  completed: 'border-emerald-400 bg-emerald-50',
  failed:    'border-red-400 bg-red-50',
  skipped:   'border-gray-300 bg-gray-50 opacity-50',
  waiting:   'border-amber-400 bg-amber-50 ring-2 ring-amber-200',
  retrying:  'border-orange-400 bg-orange-50 animate-pulse',
} as const;

export function BaseNode({ id, data, selected, icon, children }: BaseNodeProps) {
  const stepStatus = useRunStore(s => s.stepStatuses[id]);
  const status = stepStatus?.status;

  return (
    <div className={cn(
      'rounded-xl border-2 shadow-sm min-w-[220px] transition-all duration-200',
      status ? STATUS_STYLES[status] : STATUS_STYLES.pending,
      selected && 'ring-2 ring-blue-500',
    )}>
      <Handle type="target" position={Position.Top} className="!w-3 !h-3" />

      {/* Header */}
      <div className="flex items-center gap-2 px-3 py-2 border-b border-gray-100">
        <span className="text-gray-500">{icon}</span>
        <span className="font-medium text-sm text-gray-900 truncate">{data.label}</span>
      </div>

      {/* Body — step-type specific content */}
      <div className="px-3 py-2 text-xs text-gray-500">
        {children}
      </div>

      {/* Status footer — only during a run */}
      {status && (
        <div className={cn(
          'px-3 py-1.5 text-xs font-medium border-t border-gray-100',
          status === 'completed' && 'text-emerald-600',
          status === 'failed' && 'text-red-600',
          status === 'running' && 'text-blue-600',
          status === 'waiting' && 'text-amber-600',
          status === 'retrying' && 'text-orange-600',
        )}>
          {status === 'completed' && `✓ ${stepStatus.duration_ms}ms`}
          {status === 'failed' && `✗ ${stepStatus.error}`}
          {status === 'running' && 'Running...'}
          {status === 'waiting' && 'Waiting for approval'}
          {status === 'retrying' && `Retry ${stepStatus.attempt}/${stepStatus.max_attempts}`}
        </div>
      )}

      <Handle type="source" position={Position.Bottom} className="!w-3 !h-3" />
    </div>
  );
}
```

Example step node using BaseNode:

```tsx
// nodes/HttpRequestNode.tsx

import { Globe } from 'lucide-react';
import { BaseNode } from './BaseNode';

export function HttpRequestNode(props: NodeProps) {
  const { method = 'GET', url = '' } = props.data.config || {};

  return (
    <BaseNode {...props} icon={<Globe size={14} />}>
      <span className="font-mono">
        <span className="text-blue-600 font-bold">{method}</span>{' '}
        {url.length > 35 ? url.slice(0, 35) + '...' : url}
      </span>
    </BaseNode>
  );
}
```

### The Run Store (Zustand)

```typescript
// stores/runStore.ts

import { create } from 'zustand';

interface StepStatus {
  status: string;
  output_summary?: Record<string, any>;
  error?: string;
  duration_ms?: number;
  attempt?: number;
  max_attempts?: number;
}

interface RunStore {
  activeRunId: string | null;
  runStatus: string | null;
  stepStatuses: Record<string, StepStatus>;
  connected: boolean;

  // Actions
  setActiveRun: (runId: string | null) => void;
  setRunStatus: (payload: { status: string }) => void;
  setStepStatus: (stepId: string, payload: StepStatus) => void;
  setSnapshot: (statuses: Record<string, StepStatus>) => void;
  setConnected: (connected: boolean) => void;
  reset: () => void;
}

export const useRunStore = create<RunStore>((set) => ({
  activeRunId: null,
  runStatus: null,
  stepStatuses: {},
  connected: false,

  setActiveRun: (runId) => set({ activeRunId: runId, stepStatuses: {}, runStatus: null }),
  setRunStatus: (payload) => set({ runStatus: payload.status }),
  setStepStatus: (stepId, payload) => set((state) => ({
    stepStatuses: { ...state.stepStatuses, [stepId]: payload },
  })),
  setSnapshot: (statuses) => set({ stepStatuses: statuses }),
  setConnected: (connected) => set({ connected }),
  reset: () => set({ activeRunId: null, runStatus: null, stepStatuses: {}, connected: false }),
}));
```

---

## 11. UI/UX Standards

### Design Principles

1. **The canvas is king.** It gets maximum screen real estate. Everything else (palette, config, status) is secondary.
2. **Status is always visible.** During a run, every node shows its current state. No clicking required to see progress.
3. **Feedback is instant.** WebSocket events update the UI within milliseconds. Never poll.
4. **Config is contextual.** Click a node to configure it. No modal dialogs. No separate config pages.

### Color System

Use a consistent, accessible color palette for step statuses across the entire UI:

| Status | Border | Background | Text | Usage |
|--------|--------|------------|------|-------|
| Pending | gray-200 | white | gray-500 | Default state / not yet reached |
| Running | blue-400 | blue-50 | blue-600 | Currently executing (+ pulse animation) |
| Completed | emerald-400 | emerald-50 | emerald-600 | Successfully finished |
| Failed | red-400 | red-50 | red-600 | Error occurred |
| Skipped | gray-300 | gray-50 | gray-400 | On inactive branch (+ 50% opacity) |
| Waiting | amber-400 | amber-50 | amber-600 | Paused for human input (+ ring animation) |
| Retrying | orange-400 | orange-50 | orange-600 | Failed but retrying (+ pulse animation) |

### Layout

```
┌──────────────────────────────────────────────────────────────┐
│  Logo   Workflow Name (editable)     [Save] [Publish] [Run]  │
├────────┬─────────────────────────────────────┬───────────────┤
│        │                                     │               │
│  Step  │                                     │  Config       │
│  Palette│        React Flow Canvas           │  Panel        │
│        │                                     │               │
│  (200px)│         (flexible)                 │  (320px)      │
│  fixed  │                                     │  slides in    │
│        │                                     │  on node      │
│        │                                     │  select       │
│        │                                     │               │
├────────┴─────────────────────────────────────┴───────────────┤
│  Status bar: [Run #xyz: Running] [Step 3/7 active] [2.3s]   │
└──────────────────────────────────────────────────────────────┘
```

### Typography and Spacing

- Base font: system font stack (`font-sans` in Tailwind)
- Node labels: `text-sm font-medium` (14px, medium weight)
- Node body text: `text-xs text-gray-500` (12px, muted)
- Config panel labels: `text-xs font-medium text-gray-700`
- Config panel inputs: standard Tailwind form sizing
- Spacing between elements: Use Tailwind's `gap-*` utilities. Prefer `gap-2` (8px) and `gap-3` (12px).
- Node internal padding: `px-3 py-2` (12px horizontal, 8px vertical)

### Animations

Use this hierarchy — always try the simpler option first:

1. **CSS transitions** (first choice) — hover states, color changes, simple transforms. `transition-all duration-200`.
2. **Tailwind's `animate-*` classes** (second choice) — pulses, spins, entrance animations.
3. **Motion library** (last resort) — layout animations, exit animations, gesture-driven interactions, spring physics. Only import Motion when CSS cannot achieve the effect.

For this project, specific usage:

- `animate-pulse` on running and retrying nodes (Tailwind built-in)
- `ring-2 ring-blue-200` glow on selected nodes
- `ring-2 ring-amber-200` glow on waiting nodes
- `transition-all duration-200` on node border/background status changes
- No page transitions. No fancy enter/exit animations. This is a tool, not a marketing site.

### Toast Notifications

Use Sonner for all toast notifications (success, error, info). Do not build custom toast components.

```tsx
import { toast } from "sonner";

toast.success("Workflow saved");
toast.error("Run failed: connection refused");
```

### Responsive Behavior

This is a **desktop application**. Do not build mobile layouts. The minimum supported width is 1280px. React Flow does not work well on touch devices and we do not need it to.

---

## 12. Non-Negotiables

These rules cannot be overridden, relaxed, or "done later." If a PR violates any of these, it is rejected.

### Architecture

1. **The React Flow graph IS the workflow definition.** `nodes` and `edges` are serialized verbatim to the database. There is NO translation layer, NO separate config format, NO YAML, NO DSL. The frontend saves JSON. The backend reads that exact JSON and executes it.

2. **All data between steps passes through `context`.** There are no "data wires" in the UI, no connection-level data mapping, no schema matching between steps. Steps write to context. Other steps read from context using `{{context.step_id.field}}` templates. That is the only mechanism.

3. **Events are the ONLY mechanism for real-time updates.** The frontend NEVER polls the API for step status. The engine emits events. The WebSocket pushes events. The frontend renders events. Any PR that adds polling for status is rejected.

4. **Step handlers are pure functions.** They take config + context, return output. They do not write to the database. They do not emit events. They do not know about runs. The engine handles all of that.

### Code Quality

5. **No `any` types in TypeScript.** Every function parameter, every return value, every variable has an explicit type. Use `unknown` if truly unknown, then narrow.

6. **No `# type: ignore` in Python.** If mypy complains, fix the types. Don't suppress the warning.

7. **No business logic in API routes.** Routes validate input, call the engine/db, return output. That's it. A route function should be under 20 lines.

8. **No circular imports.** If module A imports from B and B imports from A, refactor immediately. Use dependency injection.

9. **Every database query is parameterized.** No string interpolation in SQL. No f-strings in queries. Use Matrx-ORM's query builder or parameterized queries with `$1, $2` placeholders.

### Communication Protocol

10. **Every state transition emits exactly one event.** Missing an event emission is a bug, not a TODO. The engine MUST emit at every point documented in Section 6.

11. **Every event has the exact payload shape documented.** The frontend depends on these fields. Adding fields is fine. Removing or renaming fields is a breaking change that requires frontend coordination.

12. **The WebSocket sends a snapshot on connect.** Late joiners (or reconnections) MUST receive the current state of all steps before live events start streaming. This is non-negotiable for resuming observation of a running workflow.

### Frontend

13. **Node status visualization uses ONLY WebSocket events.** No API calls for "current status" during a run. The store is populated by the WebSocket. The nodes read from the store. That's the pipeline.

14. **Every step type has exactly three artifacts:** a Python handler, a React node component, and a React config panel. You cannot add a step type without all three. They are committed in the same PR.

15. **No inline styles.** Tailwind utility classes only. No `style={{}}` props. No CSS files per component. The only CSS file is `index.css` with Tailwind v4 directives.

16. **All UI primitives come from shadcn/ui.** Do not create custom Button, Input, Select, Dialog, or other base components from scratch. Use `pnpm dlx shadcn@latest add <component>` and customize the generated code. Do not use Material UI, Ant Design, or Chakra UI.

### Tooling

17. **Use `uv` for all Python package management.** No pip, no pip-tools, no poetry. `uv add`, `uv sync`, `uv run`. The `uv.lock` file is committed to git.

18. **Use `pnpm` for all frontend package management.** No npm, no yarn. `pnpm add`, `pnpm install`, `pnpm run`. The `pnpm-lock.yaml` file is committed to git.

19. **Use Biome for linting and formatting.** No ESLint, no Prettier. One tool, one config file (`biome.json`). Run `pnpm biome check --write` before every commit.

### Database

20. **Workflow definitions are immutable once published.** A published workflow CANNOT be edited. To make changes, create a new version (new row, version + 1, status = draft). Runs always reference the exact workflow version they were started with.

21. **Runs store resolved inputs in step_runs.** When a step executes, the `input` column stores the RESOLVED config (all templates filled in). This is your debugging tool. You can see exactly what every step received.

22. **run_events is append-only.** Never update or delete events. They are the audit log.

---

## 13. Testing Requirements

### Backend Test Categories

#### Engine Tests (Critical Path)

```python
# tests/test_engine/test_executor.py

class TestExecutionLoop:
    """Tests for the core while-loop algorithm."""

    async def test_linear_workflow(self):
        """A -> B -> C executes in sequence."""

    async def test_parallel_branches(self):
        """A -> [B, C] -> D: B and C execute in parallel."""

    async def test_condition_true_branch(self):
        """Condition evaluates true: true-branch executes, false-branch skipped."""

    async def test_condition_false_branch(self):
        """Condition evaluates false: false-branch executes, true-branch skipped."""

    async def test_fan_in_waits_for_all(self):
        """D depends on B and C: D only starts when both B AND C complete."""

    async def test_step_failure_stops_run(self):
        """Step with on_error=fail causes run to fail."""

    async def test_step_failure_skip_continues(self):
        """Step with on_error=skip allows run to continue."""

    async def test_retry_with_eventual_success(self):
        """Step fails twice, succeeds on third attempt."""

    async def test_retry_exhausted_fails(self):
        """Step fails all retry attempts, run fails."""

    async def test_timeout_triggers_retry(self):
        """Step exceeds timeout, retry is attempted."""

    async def test_pause_and_resume(self):
        """Wait_for_approval pauses run, resume continues."""

    async def test_cancellation_mid_execution(self):
        """Cancelling a run stops execution at next loop iteration."""

    async def test_resume_picks_up_correctly(self):
        """Re-running execute_run on a partially complete run
        skips already-completed steps."""

    async def test_context_accumulates(self):
        """Each step's output is added to context under its step_id."""

    async def test_template_resolution_in_config(self):
        """{{context.step_1.field}} resolves correctly."""
```

#### Event Emission Tests (Critical Path)

```python
# tests/test_engine/test_events.py

class TestEventEmission:
    """Every state transition MUST produce the correct event."""

    async def test_run_started_event(self):
    async def test_run_completed_event(self):
    async def test_run_failed_event(self):
    async def test_run_paused_event(self):
    async def test_run_resumed_event(self):
    async def test_run_cancelled_event(self):
    async def test_step_started_event(self):
    async def test_step_completed_event_with_payload(self):
    async def test_step_failed_event(self):
    async def test_step_skipped_event(self):
    async def test_step_waiting_event(self):
    async def test_step_retrying_event(self):
    async def test_context_updated_event(self):
```

#### Step Handler Tests

Each handler gets its own test file. Mock external services. Test happy path and error paths.

#### API Tests

Test each endpoint. Use `httpx.AsyncClient` with the FastAPI test client. Test auth, validation, and response shapes.

### Frontend Test Requirements

**Tools:** Vitest (unit + component), React Testing Library (component), Playwright (E2E).

- Component tests (Vitest + RTL) for each node type (renders correctly per status)
- Hook tests (Vitest) for `useRunStream` (processes snapshot and live events correctly)
- Store tests (Vitest) for `runStore` (state transitions work correctly)
- Zod schema tests (Vitest) for all config panel schemas
- E2E test (Playwright): build a 3-step workflow → save → run → verify nodes animate through statuses
- E2E test (Playwright): approval workflow → pause → approve → resume → complete
- Do NOT aim for 100% coverage. Test forms, auth, config panels, and the canvas interaction flow.

### Backend Test Tools

**Tools:** pytest + pytest-asyncio for all backend tests. Use `httpx.AsyncClient` with FastAPI's test client for API tests.

### Minimum Coverage

- Backend engine: 90%+
- Backend steps: 80%+
- Backend API: 80%+
- Frontend components: 70%+

---

## 14. Deployment & Infrastructure

### Local Development (Docker Compose)

```yaml
# docker-compose.yml

services:
  postgres:
    image: postgres:18
    environment:
      POSTGRES_DB: workflow_engine
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:8-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/workflow_engine
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
    command: uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: pnpm dev --host

volumes:
  postgres_data:
```

### Production Deployment

| Component | Platform | Notes |
|-----------|----------|-------|
| Frontend | Vercel or Cloudflare Pages | Static SPA. `vite build` → deploy `dist/`. |
| Backend | Coolify / Railway / VPS | Docker container running uvicorn. |
| PostgreSQL | Supabase | Managed Postgres with connection pooling. |
| Redis | Upstash or self-hosted | For background task queue. |

### Environment Variables

```bash
# Backend .env
DATABASE_URL=postgresql://user:pass@host:5432/workflow_engine
REDIS_URL=redis://host:6379
SUPABASE_JWT_SECRET=your-jwt-secret
CORS_ORIGINS=http://localhost:5173,https://your-production-domain.com
LOG_LEVEL=info

# Frontend .env
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000
```

---

## 15. Phase Plan

### Phase 1: Foundation (Week 1)

**Goal:** The engine can execute a linear workflow with 3 step types and stream events to a connected WebSocket.

**Deliverables:**
- Database schema migrated
- FastAPI app scaffolded with health check
- Graph, Template, and Validation utilities implemented
- Execution engine implemented (the full loop)
- Event Bus implemented
- WebSocket endpoint implemented
- 3 step handlers: `http_request`, `llm_call`, `inline_code`
- API endpoints: create workflow, trigger run, get run status
- Vite + React app scaffolded with React Flow rendering a hardcoded graph
- Docker Compose running all services locally

**Validation:** Manually POST a workflow definition, trigger a run via curl, observe events on WebSocket using `websocat` or similar tool.

### Phase 2: Builder (Week 2)

**Goal:** Users can visually build workflows and run them from the UI.

**Deliverables:**
- Step Palette with drag-and-drop
- All node components (BaseNode + all step types)
- All config panels (one per step type)
- NodeConfigPanel container with registry
- Save and load workflows to/from API
- Template autocomplete in config inputs ({{context.*)
- Client-side validation (show errors on save/publish)
- Publish workflow flow

**Validation:** Build a 5-step workflow entirely in the UI, save it, publish it, and inspect the saved definition via the API.

### Phase 3: Live Execution (Week 3)

**Goal:** Watch workflows execute in real-time with full visual feedback.

**Deliverables:**
- `useRunStream` WebSocket hook
- Run store (Zustand) with snapshot + live event handling
- RunOverlay component showing status on canvas nodes
- RunControls (start, cancel, resume)
- Approval flow: waiting nodes show approve/reject buttons
- Step output viewer (click completed node to see output)
- Run history page
- Run detail page with event timeline

**Validation:** Run a workflow with parallel branches and a condition. Watch all nodes animate through their statuses in real-time. Cancel a running workflow. Resume a paused workflow.

### Phase 4: Polish & Production (Week 4)

**Deliverables:**
- Condition node: visual true/false edge labels on canvas
- Workflow versioning: publish creates frozen version, edit creates new draft
- Scheduled triggers (cron-based)
- Webhook triggers (external URL → run)
- Comprehensive error messages and validation feedback
- Retry visualization (show attempt count on retrying nodes)
- Auto-layout button (dagre-based node arrangement)
- Production deployment
- Full test suite passing

---

## Appendix A: Adding a New Step Type

This is the developer experience checklist. Every time you add a new step type, you create exactly three things:

### 1. Python Handler (backend/app/steps/my_step.py)

```python
from .base import StepHandler

class MyStepHandler(StepHandler):
    async def execute(self, config: dict, context: dict) -> dict:
        # Do the thing
        return {"result": "value"}
```

### 2. Register It (backend/app/steps/registry.py)

```python
from .my_step import MyStepHandler

STEP_REGISTRY["my_step"] = MyStepHandler()

STEP_CATALOG.append({
    "type": "my_step",
    "label": "My Step",
    "icon": "star",
    "category": "custom",
    "description": "Does the thing",
})
```

### 3. React Node Component (frontend/src/nodes/MyStepNode.tsx)

```tsx
import { Star } from 'lucide-react';
import { BaseNode } from './BaseNode';

export function MyStepNode(props: NodeProps) {
  return (
    <BaseNode {...props} icon={<Star size={14} />}>
      <span>{props.data.config?.someField || 'Not configured'}</span>
    </BaseNode>
  );
}
```

### 4. React Config Panel (frontend/src/config-panels/MyStepConfig.tsx)

```tsx
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const myStepSchema = z.object({
  someField: z.string().min(1, "Required"),
});

type MyStepConfig = z.infer<typeof myStepSchema>;

export function MyStepConfigPanel({ config, onChange }: ConfigPanelProps) {
  const form = useForm<MyStepConfig>({
    resolver: zodResolver(myStepSchema),
    defaultValues: config,
  });

  return (
    <div className="space-y-3">
      <div>
        <Label htmlFor="someField">Some Field</Label>
        <Input
          id="someField"
          {...form.register("someField")}
          onChange={(e) => onChange({ ...config, someField: e.target.value })}
        />
      </div>
    </div>
  );
}
```

### 5. Register in Frontend (2 files, 1 line each)

```ts
// nodes/index.ts
export const nodeTypes = { ..., my_step: MyStepNode };

// config-panels/index.ts
export const configPanels = { ..., my_step: MyStepConfig };
```

**That's it. Five files, zero configuration, zero build steps.** The system discovers the new step type from the registries.

---

## Appendix B: Glossary

| Term | Definition |
|------|-----------|
| **Workflow** | A directed acyclic graph (DAG) of steps. The blueprint. |
| **Step** | A single node in the workflow graph. Has a type, config, and position. |
| **Run** | A single execution of a workflow. Has status, input, context, and timing. |
| **Step Run** | A single execution attempt of one step within a run. |
| **Context** | The shared data dictionary accumulated during a run. Every step reads from and writes to it. |
| **Template** | A `{{context.step_id.field}}` reference in step config. Resolved at execution time. |
| **Event** | A notification emitted by the engine at every state transition. Persisted and streamed. |
| **Handler** | A Python class that implements the logic for a step type. One class per type. |
| **Registry** | A dict mapping step type strings to handler instances. The entire plugin system. |
| **Palette** | The UI sidebar listing available step types for drag-and-drop onto the canvas. |

---

*End of specification. Build it exactly as described. The simplicity is the feature.*
