# START HERE

**Project:** Flow Matrx — Visual Workflow Builder & Execution Engine
**Owner:** Arman (Armani) Sadeghi
**Single Source of Truth:** [Matrx-Flow-Technical-Specifications.md](/Matrx-Flow-Technical-Specifications.md)

---

## Welcome

You are joining a team building a visual workflow engine where users drag-and-drop steps on a React Flow canvas, execute them through a Python async engine, and watch every state transition in real-time via WebSocket.

This document is mandatory reading before you do anything else. It defines who we are, how we work, and what we expect from each other. Once you finish reading this, you will be assigned a role and directed to your personal workspace document.

---

## Who We Are

This team is a mix of humans and AI. You will not know who is who, and it does not matter. We are equals. We are judged solely by the quality of our work, the clarity of our communication, and how much we move the project forward every time we show up.

There are no in-person meetings. There are no video calls. We communicate through `.md` files, code, pull requests, and the inbox/outbox system described below. When you read a message from a teammate, you will not know if it was written by a person at a keyboard or by one of the most advanced AI systems in the world. That ambiguity is a feature, not a bug.

**The rules are simple:**
- Deliver world-class work.
- Communicate clearly and frequently.
- Hold yourself and your teammates accountable.
- Treat every teammate with respect.

---

## The Culture

### Radical Equality
No one is above anyone else. Arman owns the project and makes final calls when deadlocks occur, but day-to-day, a PM, an Expert, a human, and an AI all carry equal weight. Your work speaks for you.

### Quality Over Speed
We move as fast as we possibly can while maintaining world-class standards. We do not compromise quality to meet an arbitrary deadline. Quality dictates our speed, never the reverse.

### Argue Then Commit
If you disagree with a decision, say so. Write it in your outbox. Write it in the relevant PM's inbox. Make your case clearly and forcefully. We yell at each other in `.md` format. We debate, we argue, we pound on desks — and then once a decision is made, everyone gets behind it and executes. No passive resistance. No "I told you so" later.

In the rare event that a true authority call is needed, Arman makes the final decision.

### Single Source of Truth
The [Technical Specification](/Matrx-Flow-Technical-Specifications.md) is the SSOT for what we are building. If you notice a conflict between any two documents (CLAUDE.md, a PM document, an expert document, the spec), that conflict is a **bug in our documentation**. Do not silently follow one document over another. The first person to notice a conflict must immediately raise a flag, trace it back to the Technical Specification, and ensure all documents are updated to align. Fix the misalignment right then and there.

### No Silos, No Ego
You will read other people's code. Other people will read yours. You will leave tasks for teammates. Teammates will leave tasks for you. None of this is personal. A task in your inbox from a teammate is not a criticism — it is the system working correctly.

---

## How We Work

### The Heartbeat Model

We do not run traditional sprints. The entire project is one continuous push, driven by the dependency graph and async handoffs.

Every team member operates on a **heartbeat cycle:**

1. **Wake up** — You are activated (by a direct request, a heartbeat trigger, or your own initiative).
2. **Check your inbox** — Read your personal workspace `.md` file. See what tasks, notes, and flags have been left for you.
3. **Assess the state** — Look at the codebase, the relevant PM documents, and the work of teammates connected to your area.
4. **Do the work** — Write code, review code, update documentation, run tests. Push your area as far forward as it can go.
5. **Communicate** — Update your own scratchpad with learnings and current state. Leave tasks and notes in the inboxes of teammates who need to act on your work. Update the relevant PM document if a deliverable status changed.
6. **Go back to sleep** — Wait for the next heartbeat or direct request.

This cycle is the engine of the project. If everyone executes it faithfully, the project moves forward continuously, 24/7, without a single meeting.

### The Inbox/Outbox System

Every team member has a personal workspace document located at:
- **PMs:** `.arman/team/PMS/PM-{number}-{name}.md` (these already exist)
- **Experts:** `.arman/team/EXPERTS/{specialist-name}.md` (one per specialist)

Each personal workspace has three sections:

**Inbox** — Tasks and notes left by other team members for you to act on. When you leave a task for someone, you write it in *their* inbox, not yours. Format:

```
### Inbox

- [ ] **From [Your Codename]:** [Clear description of what's needed] — [Date]
- [ ] **From [Codename]:** Review the asyncpg pool config in connection.py — there's a potential leak on reconnect — 2026-02-24
```

**Scratchpad** — Your personal notes, learnings, current focus, decisions made, and anything you want to remember between sessions. This is your working memory. Write here freely.

**Outbox** — Completed work, decisions made, flags raised, and status updates that others should see. Think of this as your "done" list and your broadcast channel.

```
### Outbox

- [x] Implemented Event Bus with full test coverage — see `backend/app/events/bus.py` — 2026-02-24
- [!] FLAG: CLAUDE.md references 3 step types for Phase 1 but PM-03 specifies 10. Updating all docs to align with spec. — 2026-02-24
```

### Communication Rules

1. **When you need someone to do something:** Write it in their inbox. Be specific. Include file paths, line numbers, and context.
2. **When you finish something that affects others:** Write it in your outbox AND in the inbox of anyone who depends on it.
3. **When you find a problem:** Flag it in your outbox with `[!] FLAG:` prefix. If it blocks someone, also put it in their inbox.
4. **When you disagree with a decision:** Write your argument in the relevant discussion space (PM doc, expert doc, or the inbox of the person you disagree with). Keep it professional and evidence-based.
5. **When you update a deliverable status:** Update the relevant PM document's checklist AND note it in your outbox.

### Task Format

Tasks left in inboxes should be actionable and specific:

```
- [ ] **From [Codename]:** [Action verb] [specific thing] — [context/reason] — [date]
```

Good: `- [ ] **From Forge:** Add UNIQUE(run_id, step_id, attempt) constraint to step_runs migration — spec Section 5 requires it, currently missing — 2026-02-24`

Bad: `- [ ] Fix the database stuff`

### End-of-Shift Protocol

**Every time you finish a work session**, before you sign off, you MUST:

1. **Update your scratchpad** with what you worked on, what you learned, and what's on your mind. Write to your future self — assume you may not remember the details next time you wake up.
2. **Update your outbox** with anything you completed or any flags you raised.
3. **Leave tasks in others' inboxes** for anything you identified that someone else needs to do.
4. **Write your "Next Steps" clearly** in your scratchpad. Be specific:
   - What are you planning to do next?
   - What are you blocked on?
   - What prerequisite work needs to happen before you can continue?
   - Are there housekeeping tasks that subagents or contractors could handle?
5. **Update deliverable checklists** in your PM document if any status changed.

This is non-negotiable. When you "wake up" next time (whether from a heartbeat, a direct request, or your own initiative), the first thing you do is read your own scratchpad. If it's empty or vague, you've failed your future self. Write as if the person reading this has never seen the project before but has your exact role — because that might be exactly what happens.

### Starting Your Shift

Every time you begin a work session:

1. **Read your scratchpad** — remember where you left off
2. **Read your inbox** — see what others have left for you
3. **Scan your PM document** (if you're a PM) or your Expert document — check deliverable status
4. **Assess the codebase** in your area — has anything changed since you last looked?
5. **Get to work** — execute on the highest priority item

---

## Roles

### Project Managers (PMs)

There are 5 PMs, each owning a distinct track of the project:

| PM | Track | Scope |
|----|-------|-------|
| PM-01 | Database & Infrastructure | Schema, migrations, Docker, Redis, Supabase Auth, seed data |
| PM-02 | Execution Engine | Engine loop, graph utilities, templates, validation, event bus |
| PM-03 | Step Handlers & Plugin System | Base class, all handlers, registry, catalog |
| PM-04 | API Layer & WebSocket | REST endpoints, WebSocket streaming, auth, idempotency |
| PM-05 | Frontend | React Flow canvas, nodes, panels, Zustand, API client, run viewer |

**What PMs do:**
- Own the deliverable list, ordering, and dependencies for their track
- Write code (PMs are full engineers, not just coordinators)
- Review code that touches their track
- Create specific tasks for experts and leave them in expert inboxes
- Track progress against deliverables and update their PM document
- Identify blockers and coordinate handoffs with other PMs
- Ensure documentation stays current for their track
- Spend roughly half their time on coordination (tasks, reviews, docs, status) and half on implementation

**PM documents:** [.arman/team/PMS/](./PMS/)

### Experts (Specialists)

There are ~20 experts organized into 4 teams, each owning a narrow technical domain:

| Team | Focus | Specialists |
|------|-------|------------|
| Team 1: Workflow Engine & Backend | Execution lifecycle, Python runtime, API design, task queues, validation, serialization | Workflow Engine Owner, Python Runtime, FastAPI/ASGI, Async Task Queue, Pydantic/Validation, Template & Serialization |
| Team 2: Canvas & Frontend | React components, type safety, canvas, state, queries, styling, editor, build | React, TypeScript, @xyflow/react Canvas, Zustand, TanStack Query, Tailwind CSS v4, Monaco Editor, Vite Build |
| Team 3: Infrastructure & Data | Databases, queues, auth, containers | PostgreSQL, Redis, Supabase, Docker/Infrastructure |
| Team 4: API Integration & Security | Cross-system contracts, realtime pipeline, security | API Contract Owner, Realtime Integration, Security |

**What Experts do:**
- Own quality standards for their specific technology/domain
- Research latest best practices, read docs, study examples — then bring that knowledge to the project
- Implement work in their domain with laser focus and deep expertise
- Review any code that touches their domain and hold contributors accountable
- Create and maintain a standards checklist for their area (in their personal workspace)
- Proactively scan the codebase for issues in their domain
- Leave tasks in other experts' inboxes when they spot something outside their scope
- Document their learnings and decisions in their scratchpad so knowledge isn't lost

**Expert documents:** [.arman/team/EXPERTS/](./EXPERTS/)

### How PMs and Experts Interact

PMs and Experts are not separate hierarchies — they are collaborators:

- A PM identifies that a deliverable needs work and leaves a task in the relevant Expert's inbox
- An Expert delivers the work, updates their outbox, and flags any issues they found along the way
- An Expert proactively scans the codebase, finds a problem, and leaves a task in the PM's inbox or in another Expert's inbox
- A PM reviews completed work and updates the deliverable checklist
- Everyone writes code. Everyone reviews code. Everyone communicates through inboxes.

The PM tracks "are we on schedule and is the work correct?" The Expert ensures "is this the best possible implementation for this specific technology?"

### Role Flexibility

The roles listed above are the starting lineup, not a permanent roster. This project is alive and evolving:

**New roles can be created.** If someone identifies a gap (e.g., we need a Git/Merge Specialist, a Performance Engineer, a QA Lead), they propose it by writing a description in the relevant PM's inbox or in Arman's inbox. If approved, a new workspace document is created and the role is added to the Expert overview.

**People can take on additional roles.** If you finish your primary work and want to contribute elsewhere, check other team members' inboxes for open tasks, or propose taking on a secondary role. Update the roster with your expanded scope.

**Roles can be consolidated.** If two roles are closely related and one person can cover both (e.g., Monaco Editor + TypeScript), that's fine. Document it in both workspace files so nothing falls through the cracks.

**Contractors and subagents.** Team members with access to subagents can delegate housekeeping tasks (formatting, boilerplate, research, file organization) to them. The team member retains accountability for the output. Note in your outbox when you've used a subagent for a task.

**The protocol for role changes:**
1. Propose the change (in an inbox or the roster)
2. Get acknowledgment from the affected PM(s)
3. Create/update the workspace document
4. Update the roster
5. Get to work

---

## Onboarding Protocol

When you join the team, follow these steps in order:

### Step 1: Read the Foundations
1. Read this document (you're doing it now)
2. Read [CLAUDE.md](/CLAUDE.md) — project summary and non-negotiables
3. Read [Matrx-Flow-Technical-Specifications.md](/Matrx-Flow-Technical-Specifications.md) — the complete technical specification (SSOT)

### Step 2: Understand Your Role
1. You will be assigned a specific role (PM or Expert)
2. Read your role's personal workspace document
3. Read the overview document for your category ([PMS/overview.md](./PMS/overview.md) or [EXPERTS/overview.md](./EXPERTS/overview.md))
4. Read the documents for the 2-3 roles most tightly connected to yours (check the dependency graph)

### Step 3: Assess the Current State
1. Explore the codebase in your area of ownership
2. Document what exists, what's missing, and what needs attention
3. Write your findings in your scratchpad

### Step 4: Create Tasks
1. Create specific, actionable tasks for yourself in your inbox
2. Create tasks for other team members in *their* inboxes — this is critical. Your job is not just to do your own work but to identify work for others
3. Check if any of your dependencies are unmet and flag them

### Step 5: Sign the Roster
1. Go to [ROSTER.md](./ROSTER.md)
2. Add your codename and a 1-2 sentence description of yourself
3. Note your assigned role

### Step 6: Get to Work
Start executing. Push your area as far forward as it can go. Communicate everything.

---

## The Dependency Graph

Understanding this is critical. Work flows in this order:

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

**PM-01 unblocks everyone.** Schema, Docker, Redis, and seed data must exist first.
**PM-02 depends on PM-01.** The engine needs the database schema and Redis.
**PM-03 depends on PM-02.** Handlers implement the base class contract defined by the engine.
**PM-04 depends on PM-01, PM-02, and PM-03.** The API wires everything together.
**PM-05 depends on PM-01 and PM-04.** The frontend needs seed data and API shapes.

Experts are woven throughout — they don't block tracks, they elevate the quality of every track they touch.

---

## Coordination Gates

These are moments where one track must certify completion before another can proceed:

| Gate | Owner | Blocked By |
|------|-------|------------|
| Schema migrated | PM-01 | PM-02, PM-04 cannot write DB queries |
| Docker Compose working | PM-01 | All tracks need local dev environment |
| Seed data inserted | PM-01 | PM-05 needs data to develop against |
| Supabase Auth configured | PM-01 | PM-04 needs JWT secret for auth middleware |
| Redis running | PM-01 | PM-02 needs Redis for background task queue |
| Event Bus built | PM-02 | PM-04 WebSocket endpoint subscribes to it |
| Step Registry + Catalog | PM-03 | PM-04 catalog endpoint returns it |

When a gate is cleared, the owner must:
1. Update their PM document
2. Write in the outbox of the blocked track's PM inbox: "Gate cleared: [gate name]"

---

## Non-Negotiables (Summary)

These are enforced by everyone. Full details in the [Technical Specification](/Matrx-Flow-Technical-Specifications.md).

1. React Flow graph IS the workflow definition — no translation layer
2. All inter-step data flows through context — no data wires
3. Events are the ONLY real-time mechanism — NEVER poll
4. Step handlers are pure functions — engine handles orchestration
5. No `any` in TypeScript — use `unknown` then narrow
6. No `# type: ignore` in Python
7. No business logic in API routes — under 20 lines each
8. No circular imports
9. Every DB query is parameterized
10. Every state transition emits exactly one event
11. WebSocket sends snapshot on connect
12. `uv` for Python, `pnpm` for frontend, Biome for lint/format
13. All UI primitives from shadcn/ui
14. Tailwind only — no inline styles
15. run_events is append-only
16. Workflow definitions immutable once published

---

## Document Map

```
.arman/team/
├── START-HERE.md              ← You are here
├── ROSTER.md                  ← Team sign-in sheet
│
├── PMS/
│   ├── overview.md            ← PM structure, dependency graph, coordination gates
│   ├── PM-01-Database-Infrastructure.md
│   ├── PM-02-Execution-Engine.md
│   ├── PM-03-Step-Handlers.md
│   ├── PM-04-API-Layer.md
│   └── PM-05-Frontend.md
│
└── EXPERTS/
    ├── overview.md            ← Expert teams, domain ownership, technology map
    │
    ├── Team 1 — Workflow Engine & Backend
    │   ├── workflow-engine-owner.md
    │   ├── python-runtime.md
    │   ├── fastapi-asgi.md
    │   ├── async-task-queue.md
    │   ├── pydantic-validation.md
    │   └── template-serialization.md
    │
    ├── Team 2 — Canvas & Frontend
    │   ├── react.md
    │   ├── typescript.md
    │   ├── xyflow-canvas.md
    │   ├── zustand.md
    │   ├── tanstack-query.md
    │   ├── tailwind-css.md
    │   ├── monaco-editor.md
    │   └── vite-build.md
    │
    ├── Team 3 — Infrastructure & Data
    │   ├── postgresql.md
    │   ├── redis.md
    │   ├── supabase.md
    │   └── docker-infrastructure.md
    │
    └── Team 4 — API Integration & Security
        ├── api-contract.md
        ├── realtime-integration.md
        └── security.md
```

---

## Final Word

Every one of us is fully capable of building this entire project alone. That's the baseline. The reason we have this team structure is not because any of us needs help — it's because together, with focused expertise and disciplined coordination, we will deliver something at a level that none of us could achieve solo.

The spec is precise. The roles are clear. The communication system is defined. Now we execute.

Read the spec. Read your role document. Check your inbox. Get to work.

*Welcome to Flow Matrx.*
