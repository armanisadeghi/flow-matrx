# Flow Matrx — Project Management Plan

Five project managers own distinct tracks with clear deliverables, dependencies, and handoffs. Each PM is a full engineer who writes code AND coordinates their track.

---

## The Five Tracks

| PM | Track | Scope | Critical Output |
|----|-------|-------|-----------------|
| **PM-01** | Database & Infrastructure | Schema, migrations, Docker, Redis, Supabase Auth, seed data | 4 tables migrated, Docker Compose running, seed workflows |
| **PM-02** | Execution Engine | Engine loop, graph utilities, templates, validation, event bus | `WorkflowEngine`, Event Bus, validation function |
| **PM-03** | Step Handlers & Plugin System | Base class, 10 handlers, registry, catalog | `STEP_REGISTRY`, `STEP_CATALOG`, all handler implementations |
| **PM-04** | API Layer & WebSocket | REST endpoints, WebSocket streaming, auth, idempotency | 18 REST routes, `WS /ws/runs/{id}` |
| **PM-05** | Frontend | React Flow canvas, nodes, panels, Zustand, API client, run viewer | 4 pages, live execution UI, WebSocket hook |

---

## What PMs Do

A PM is not just a coordinator — they are a full engineer with management responsibilities:

**~50% Implementation**
- Write production code in their track
- Write tests for their track
- Fix bugs in their track

**~50% Coordination**
- Review code that touches their track
- Create specific, actionable tasks for Experts and leave them in Expert inboxes
- Track progress against deliverables and update their PM document
- Identify blockers and coordinate handoffs with other PMs
- Ensure documentation stays current
- Verify that coordination gates are met before signaling "clear"

---

## Dependency Graph

```
PM-01 (Database & Infrastructure)
    |
    ├──> PM-02 (Execution Engine) ──────────────┐
    |         |                                  |
    |         └──> PM-03 (Step Handlers)         |
    |                    |                       |
    |                    └───────────────────────┼──> PM-04 (API Layer) ──> PM-05 (Frontend)
    |                                            |
    └────────────────────────────────────────────┘
```

- **PM-01** is the root. Schema, Docker, Redis, Supabase Auth, and seed data must exist before anyone can write DB queries or develop against real data.
- **PM-02** depends on PM-01 (schema, Redis). PM-03 depends on PM-02 (base class contract).
- **PM-04** depends on PM-01, PM-02, and PM-03. It consumes the engine, event bus, validation, and step catalog.
- **PM-05** depends on PM-01 (seed data) and PM-04 (API shapes, WebSocket format, catalog).

---

## Coordination Gates

| Gate | Owner | Blocked Tracks |
|------|-------|----------------|
| Schema migrated | PM-01 | PM-02, PM-04 |
| Docker Compose working | PM-01 | All |
| Seed data inserted | PM-01 | PM-05 |
| Supabase Auth configured | PM-01 | PM-04 |
| Redis running | PM-01 | PM-02 |
| Event Bus built | PM-02 | PM-04 (WebSocket) |
| Step Registry + Catalog | PM-03 | PM-04 (catalog endpoint) |

**When a gate is cleared:**
1. Update the deliverable checklist in your PM document
2. Write in the blocked PM's inbox: "Gate cleared: [gate name]"
3. Note it in your outbox

---

## PM ↔ Expert Interaction

PMs and Experts are collaborators, not separate hierarchies:

- **PM → Expert:** PM identifies a deliverable that needs deep expertise. PM writes a specific task in the Expert's inbox.
- **Expert → PM:** Expert completes the work, updates their outbox, and flags any issues found. PM reviews and updates deliverable status.
- **Expert → PM (proactive):** Expert scans the codebase, finds a problem in the PM's track, writes a task or flag in the PM's inbox.
- **Cross-expert:** An Expert finds something outside their scope and leaves it in another Expert's inbox directly.

The PM tracks "are we on schedule and is the work correct?" The Expert ensures "is this the best possible implementation for this specific technology?"

---

## Key Principles (Cross-Track)

1. **Events are the only real-time mechanism** — no polling. Engine emits; WebSocket streams; frontend renders.
2. **Handlers are pure** — no DB writes, no event emission. Engine owns orchestration.
3. **Context is the scratchpad** — all inter-step data flows through `runs.context` via templates.
4. **Routes are thin** — under 20 lines, no business logic. Validate → call engine/db → return.
5. **Snapshot on WebSocket connect** — late joiners and reconnections get current state before live events.

---

## Success Criteria (Aggregate)

- [ ] All 4 tables migrated, Matrx-ORM models match schema
- [ ] Engine executes linear, parallel, and conditional workflows end-to-end
- [ ] Every state transition emits the correct event with correct payload
- [ ] All 10 step handlers implemented with 80%+ coverage
- [ ] All 18 REST endpoints + WebSocket implemented with 80%+ coverage
- [ ] React Flow canvas with live run visualization
- [ ] `make dev` brings up full stack; seed workflows run successfully

---

## Document Index

- [PM-01: Database & Infrastructure](./PM-01-Database-Infrastructure.md)
- [PM-02: Execution Engine](./PM-02-Execution-Engine.md)
- [PM-03: Step Handlers & Plugin System](./PM-03-Step-Handlers.md)
- [PM-04: API Layer & WebSocket](./PM-04-API-Layer.md)
- [PM-05: Frontend](./PM-05-Frontend.md)
