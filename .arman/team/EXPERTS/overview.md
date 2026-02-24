# Flow Matrx — Expert Team Structure

~20 specialists organized into 4 teams. Each Expert owns a narrow technical domain with depth that no generalist can match. They implement, review, hold standards, and leave the codebase better every time they touch it.

---

## The Four Teams

### Team 1: Workflow Engine & Backend
Owns execution lifecycle, task orchestration, Python runtime, API layer, and data validation.

### Team 2: Canvas & Frontend
Owns the workflow canvas, client state, UI build pipeline, and code editing interface.

### Team 3: Infrastructure & Data
Owns databases, queues, auth, containerization, and migrations.

### Team 4: API Integration & Security
Owns cross-system contracts, realtime status pipeline, and security boundaries.

---

## What Experts Do

Every Expert operates on the heartbeat cycle described in [START-HERE.md](../START-HERE.md):

1. **Research** — Stay current on their technology. Read docs, study examples, know the latest best practices.
2. **Implement** — Write production code in their domain with laser focus and deep expertise.
3. **Review** — Scan the codebase for issues in their domain. Review any code that touches their area.
4. **Hold Standards** — Maintain a standards checklist in their personal workspace. Hold every contributor accountable to it.
5. **Communicate** — Leave tasks in other experts' and PMs' inboxes. Document learnings in their scratchpad. Update their outbox with completed work.

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
| Zustand 5.0.11 | Zustand Specialist | Store architecture, workflow graph state, slice boundaries |
| TanStack Query 5.90.21 | TanStack Query Specialist | Query key design, cache invalidation, execution status polling strategy |
| Tailwind CSS v4.2.0 | Tailwind CSS Specialist | CSS-first config, @theme directive system, elimination of tailwind.config.js |
| @monaco-editor/react 4.6.0 | Monaco Editor Specialist | Editor integration for inline_code nodes, language server config, keybinding safety |
| Vite 7.3.1 | Vite Build Specialist | Build config, code splitting, hot reload, production bundle optimization |
| Docker | Docker/Infrastructure Specialist | Service orchestration, environment parity, image layering, secret management |
| httpx 0.28.1 | FastAPI/ASGI Specialist | Async HTTP client usage for external AI service calls, timeout/retry config |
| structlog 24.4.0 | Python Runtime Specialist | Structured log schema, context propagation across async boundaries |

---

## Lead Structure

Each team has a lead (denoted by their dual role). Leads coordinate within their team but have no special authority — they are first among equals.

```
Team 1: Workflow Engine & Backend — Lead: Workflow Execution Engine Owner
├── Python Runtime Specialist
├── FastAPI/ASGI Specialist
├── Async Task Queue Specialist
├── Pydantic/Validation Specialist
└── Template & Serialization Specialist

Team 2: Canvas & Frontend — Lead: React Specialist
├── TypeScript Specialist
├── @xyflow/react Canvas Specialist
├── Zustand Specialist
├── TanStack Query Specialist
├── Tailwind CSS v4 Specialist
├── Monaco Editor Specialist
└── Vite Build Specialist

Team 3: Infrastructure & Data — Lead: PostgreSQL Specialist
├── Redis Specialist
├── Supabase Specialist
└── Docker/Infrastructure Specialist

Team 4: API Integration & Security — Lead: API Contract Owner
├── Realtime Integration Specialist
└── Security Specialist
```

---

## Expert ↔ PM Mapping

Experts work across PM tracks depending on what's being built:

| Expert | Primary PM | Secondary PMs |
|--------|-----------|---------------|
| Workflow Engine Owner | PM-02 | PM-04 |
| Python Runtime | PM-02 | PM-03 |
| FastAPI/ASGI | PM-04 | PM-02 |
| Async Task Queue | PM-02 | PM-01 |
| Pydantic/Validation | PM-04 | PM-02, PM-03 |
| Template & Serialization | PM-02 | PM-03 |
| React | PM-05 | — |
| TypeScript | PM-05 | — |
| @xyflow/react Canvas | PM-05 | — |
| Zustand | PM-05 | — |
| TanStack Query | PM-05 | — |
| Tailwind CSS v4 | PM-05 | — |
| Monaco Editor | PM-05 | — |
| Vite Build | PM-05 | — |
| PostgreSQL | PM-01 | PM-02 |
| Redis | PM-01 | PM-02 |
| Supabase | PM-01 | PM-04 |
| Docker/Infrastructure | PM-01 | — |
| API Contract Owner | PM-04 | PM-05 |
| Realtime Integration | PM-04 | PM-02, PM-05 |
| Security | PM-04 | PM-02, PM-03 |

---

## Individual Workspace Documents

Every Expert has a personal workspace document at `.arman/team/EXPERTS/{name}.md` with three sections: **Inbox**, **Scratchpad**, and **Outbox**. See [START-HERE.md](../START-HERE.md) for how these work.

### Team 1: Workflow Engine & Backend
- [Workflow Execution Engine Owner](./workflow-engine-owner.md)
- [Python Runtime Specialist](./python-runtime.md)
- [FastAPI/ASGI Specialist](./fastapi-asgi.md)
- [Async Task Queue Specialist](./async-task-queue.md)
- [Pydantic/Validation Specialist](./pydantic-validation.md)
- [Template & Serialization Specialist](./template-serialization.md)

### Team 2: Canvas & Frontend
- [React Specialist](./react.md)
- [TypeScript Specialist](./typescript.md)
- [@xyflow/react Canvas Specialist](./xyflow-canvas.md)
- [Zustand Specialist](./zustand.md)
- [TanStack Query Specialist](./tanstack-query.md)
- [Tailwind CSS v4 Specialist](./tailwind-css.md)
- [Monaco Editor Specialist](./monaco-editor.md)
- [Vite Build Specialist](./vite-build.md)

### Team 3: Infrastructure & Data
- [PostgreSQL Specialist](./postgresql.md)
- [Redis Specialist](./redis.md)
- [Supabase Specialist](./supabase.md)
- [Docker/Infrastructure Specialist](./docker-infrastructure.md)

### Team 4: API Integration & Security
- [API Contract Owner](./api-contract.md)
- [Realtime Integration Specialist](./realtime-integration.md)
- [Security Specialist](./security.md)

---

## Coverage Gaps

**Monaco Editor + TypeScript Specialist overlap risk.** These may be the same person. Risk: Monaco configuration complexity may not receive adequate attention if the TypeScript specialist is occupied with codebase-wide type enforcement during the TS 6 migration.

**Template & Serialization Specialist is narrow.** If team size requires consolidation, this role is most safely absorbed into the Pydantic/Validation Specialist. Risk: Jinja2 template injection edge cases receive less scrutiny.

**No dedicated Performance Engineer.** Performance ownership is distributed — Python Runtime owns backend throughput, Vite Build owns bundle size, Canvas Specialist owns render performance. Risk: system-wide performance regressions that cross team boundaries have no single owner.

**No dedicated QA/Test Automation Engineer.** Testing ownership is distributed across domain owners. Risk: complex integration tests (async execution + canvas state sync + WebSocket) may fall through the cracks.
