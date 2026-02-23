# AI Matrx Workflow Engine — Team Structure

---

## Teams

### Team 1: Workflow Engine & Backend
Owns execution lifecycle, task orchestration, Python runtime, API layer, and data validation.

### Team 2: Canvas & Frontend
Owns the workflow canvas, client state, UI build pipeline, and code editing interface.

### Team 3: Infrastructure & Data
Owns databases, queues, auth, containerization, and migrations.

### Team 4: API Integration & Security
Owns cross-system contracts, realtime status pipeline, and security boundaries.

---

## Domain Ownership Map

| Failure Domain | Owner | What They Prevent |
|---|---|---|
| Workflow execution lifecycle | Workflow Execution Engine Owner | Stalled workflows, lost execution state, incorrect node dispatch order |
| Python subinterpreter isolation | Python Runtime Specialist | Code bleed between executions, GIL violations, inline_code handler memory leaks |
| Async task queue reliability | Async Task Queue Specialist | Silent job drops, retry storms, arq worker desync from Redis queue |
| Workflow state persistence | PostgreSQL Specialist | Partial writes, migration regressions, workflow graph corruption in DB |
| Client-side state consistency | Zustand State Management Specialist | Canvas state diverging from server state, stale workflow graph in UI |
| Realtime status propagation | Realtime Integration Specialist | Execution status never reaching the frontend, PubSub channel leaks |
| Code execution sandbox | Security Specialist | Inline code escaping its execution context, auth boundary violations |
| API contract stability | API Contract Owner | Breaking schema changes silently reaching consumers |
| Canvas render correctness | @xyflow/react Canvas Specialist | v12 node measurement failures, dagre layout producing invalid graphs |

---

## Technology Ownership Map

| Tool / Framework | Specialist | What They Enforce |
|---|---|---|
| Python 3.14 + subinterpreters | Python Runtime Specialist | PEP 734 subinterpreter lifecycle, asyncio event loop hygiene, import isolation |
| FastAPI 0.131 + uvicorn 0.41 | FastAPI/ASGI Specialist | Route design, middleware ordering, ASGI lifecycle, worker configuration |
| asyncpg 0.31 | PostgreSQL Specialist | Connection pool configuration, query correctness, driver-level error handling |
| Pydantic v2.12 + pydantic-settings | Pydantic/Validation Specialist | Schema contracts, strict model design, settings validation at startup |
| arq 0.27 | Async Task Queue Specialist | Worker pool sizing, job serialization, retry policy, Redis backing config |
| Jinja2 3.1.5 + orjson 3.11.7 | Template & Serialization Specialist | Template injection safety, dynamic node input resolution, fast JSON correctness |
| PostgreSQL 18.2 + Alembic 1.18.4 | PostgreSQL Specialist | Schema migrations, v18 regression monitoring (18.3 patch), index strategy |
| Redis 8.0.10 | Redis Specialist | PubSub channel design, arq queue backing, eviction policy, persistence config |
| Supabase (Auth + Hosting) | Supabase Specialist | RLS policies, JWT validation integration, hosted environment configuration |
| React 19.0.0 | React Specialist | Component architecture, concurrent rendering patterns, React 19 feature usage |
| TypeScript 5.9/6.0 | TypeScript Specialist | Strict mode enforcement, type coverage across entire codebase, TS 6 migration |
| @xyflow/react 12.10.0 + dagre 1.1.0 | Canvas Specialist | v12 measured node system, custom node/edge types, auto-layout correctness |
| Zustand 5.0.11 | Zustand State Management Specialist | Store architecture, workflow graph state, slice boundaries |
| TanStack Query 5.90.21 | TanStack Query Specialist | Query key design, cache invalidation, execution status polling strategy |
| Tailwind CSS v4.2.0 | Tailwind CSS Specialist | CSS-first config, @theme directive system, elimination of tailwind.config.js |
| @monaco-editor/react 4.6.0 | Monaco Editor Specialist | Editor integration for inline_code nodes, language server config, keybinding safety |
| Vite 7.3.1 | Vite Build Specialist | Build config, code splitting, hot reload, production bundle optimization |
| Docker | Docker/Infrastructure Specialist | Service orchestration, environment parity, image layering, secret management |
| httpx 0.28.1 | FastAPI/ASGI Specialist | Async HTTP client usage for external AI service calls, timeout/retry config |
| structlog 24.4.0 | Python Runtime Specialist | Structured log schema, context propagation across async boundaries |

---

## Specialist Roles

### Team 1: Workflow Engine & Backend

**Workflow Execution Engine Owner**
Owns the core execution state machine — node dispatch order, handler routing, execution lifecycle hooks, and failure recovery paths. Holds all backend engineers accountable for preserving execution invariants. The single decision-maker on what constitutes a valid workflow execution state.

**Python Runtime Specialist**
Owns Python 3.14 internals and PEP 734 subinterpreter architecture for the `inline_code` handler. Responsible for subinterpreter lifecycle management, preventing interpreter state bleed, asyncio event loop ownership per execution context, and structlog context propagation across async boundaries. Catches runtime-level issues no other specialist will see.

**FastAPI/ASGI Specialist**
Owns FastAPI route design, dependency injection patterns, middleware ordering, and uvicorn configuration. Responsible for correct ASGI lifecycle behavior, request validation pipeline, and httpx client configuration for external AI service calls. Holds all backend contributors accountable for route-level correctness.

**Async Task Queue Specialist**
Owns arq worker design end-to-end — job registration, serialization contracts, retry policy, dead-letter behavior, and Redis queue backing configuration. Prevents silent job loss and worker desync. The single owner of anything that runs outside the request/response cycle.

**Pydantic/Validation Specialist**
Owns all Pydantic v2 model and schema design across the backend. Responsible for strict model enforcement, pydantic-settings startup validation, and ensuring serialization contracts match what asyncpg and FastAPI expect. Prevents schema drift between layers.

**Template & Serialization Specialist**
Owns Jinja2 template resolution for dynamic workflow node inputs and orjson serialization throughout the backend. Responsible for template injection safety, dynamic input rendering correctness, and JSON serialization performance and correctness. Catches the subtle edge cases in template rendering that generalists miss.

---

### Team 2: Canvas & Frontend

**React Specialist**
Owns React 19 component architecture, concurrent rendering patterns, and React 19-specific feature adoption. Responsible for component lifecycle correctness, rendering performance, and ensuring the team does not misuse concurrent features. Holds frontend contributors accountable for idiomatic React 19 usage.

**TypeScript Specialist**
Owns type safety across the entire frontend codebase. Enforces strict mode, manages the TypeScript 5.9 → 6.0 transition (stricter defaults, `strict: true` by default), and owns the type definitions at every API boundary. Every team member is accountable to this specialist for typing violations.

**@xyflow/react Canvas Specialist**
Owns the workflow canvas implementation using @xyflow/react v12. Responsible for the v12 "measured" node dimension system, custom node and edge type implementations, dagre-driven auto-layout integration, and canvas performance under large workflow graphs. The single owner of all canvas behavioral correctness.

**Zustand State Management Specialist**
Owns the Zustand 5 store architecture for client-side workflow state. Responsible for store slice design, workflow graph state ownership, and ensuring canvas state and server state remain synchronized. Prevents state proliferation and stale graph scenarios.

**TanStack Query Specialist**
Owns all server state management via TanStack Query 5. Responsible for query key hierarchy design, cache invalidation strategy, and the polling mechanism that delivers workflow execution status to the UI. Holds the boundary between server state and client state.

**Tailwind CSS v4 Specialist**
Owns the CSS-first Tailwind v4 configuration — `@theme` directives, design token definitions, and the elimination of `tailwind.config.js`. Responsible for design system consistency and ensuring all contributors use v4 patterns rather than v3 habits. Catches v4-specific breakage early.

**Monaco Editor Specialist**
Owns the Monaco editor integration for `inline_code` workflow nodes. Responsible for language server configuration, syntax highlighting, keybinding safety, and ensuring the editor does not interfere with canvas event handling. A narrow but high-complexity integration requiring dedicated ownership.

**Vite Build Specialist**
Owns the Vite 7 build pipeline — dev server config, code splitting strategy, environment variable handling, and production bundle optimization. Responsible for build reproducibility and ensuring TypeScript and Tailwind v4 toolchains integrate cleanly under Vite.

---

### Team 3: Infrastructure & Data

**PostgreSQL Specialist**
Owns PostgreSQL 18.2 schema design, query optimization, Alembic migration strategy, and asyncpg connection pool configuration. Monitors the 18.3 regression patch (substring fix) and owns the decision on when to upgrade. Responsible for workflow graph persistence correctness and migration safety.

**Redis Specialist**
Owns Redis 8.0.10 configuration for both the arq task queue backing store and PubSub channel architecture for workflow execution status. Responsible for eviction policy, persistence mode, and channel design that supports the realtime status pipeline. Holds arq and PubSub integration jointly accountable.

**Supabase Specialist**
Owns Supabase auth integration — JWT validation, Row-Level Security policy design, and hosted environment configuration. Responsible for ensuring RLS policies correctly restrict workflow data access and that auth flows integrate cleanly with FastAPI's dependency injection.

**Docker/Infrastructure Specialist**
Owns containerization and service orchestration for the full stack — Python backend, Redis, PostgreSQL, and frontend build. Responsible for environment parity between development and production, image layering strategy, and secret management. Ensures no service dependency is unresolved at startup.

---

### Team 4: API Integration & Security

**API Contract Owner**
Owns the OpenAPI schema generated by FastAPI and all interface definitions between frontend and backend. Responsible for preventing breaking changes from reaching consumers silently, maintaining versioning discipline, and ensuring TanStack Query's server state expectations match actual API responses. The single enforcer of interface stability.

**Realtime Integration Specialist**
Owns the complete realtime pipeline: Redis PubSub → backend event emission → WebSocket or SSE transport → TanStack Query invalidation or Zustand update in the frontend. This cross-boundary pipeline is the highest integration-complexity point in the system and requires a single owner who understands every layer of it.

**Security Specialist**
Owns the security posture of the system with primary focus on the `inline_code` execution sandbox. Responsible for ensuring subinterpreter or process isolation prevents user-submitted code from accessing host resources, validates Supabase JWT enforcement at API boundaries, and audits Jinja2 templates for injection risk. Code execution isolation is the highest-severity attack surface in this project.

---

## Lead Structure

```
Workflow Engine & Backend Lead (Workflow Execution Engine Owner)
├── Python Runtime Specialist
├── FastAPI/ASGI Specialist
├── Async Task Queue Specialist
├── Pydantic/Validation Specialist
└── Template & Serialization Specialist

Canvas & Frontend Lead (React Specialist)
├── TypeScript Specialist
├── @xyflow/react Canvas Specialist
├── Zustand State Management Specialist
├── TanStack Query Specialist
├── Tailwind CSS v4 Specialist
├── Monaco Editor Specialist
└── Vite Build Specialist

Infrastructure & Data Lead (PostgreSQL Specialist)
├── Redis Specialist
├── Supabase Specialist
└── Docker/Infrastructure Specialist

API Integration & Security Lead (API Contract Owner)
├── Realtime Integration Specialist
└── Security Specialist
```

---

## Coverage Gaps

**Monaco Editor + TypeScript Specialist overlap risk.** For medium scale, these may be the same person. Risk: Monaco configuration complexity (language servers, worker threads, canvas event conflicts) may not receive adequate attention if the TypeScript specialist is occupied with codebase-wide type enforcement during the TS 6 migration.

**Template & Serialization Specialist is narrow.** If team size requires consolidation, this role is most safely absorbed into the Pydantic/Validation Specialist. Risk: Jinja2 template injection edge cases and orjson serialization correctness receive less scrutiny under a generalist.

**No dedicated Performance Engineer.** At medium scale, performance ownership is distributed — Python Runtime Specialist owns backend throughput, Vite Build Specialist owns bundle size, and the Canvas Specialist owns render performance. Risk: system-wide performance regressions that cross team boundaries have no single owner to catch them holistically.

**No dedicated QA/Test Automation Engineer.** Workflow execution correctness testing — especially for async job execution, subinterpreter behavior, and canvas state sync — is complex enough to warrant dedicated ownership. Currently assumed to be distributed across domain owners, which is a gap for a workflow engine where execution correctness is the core product guarantee.