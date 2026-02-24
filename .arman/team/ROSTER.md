# Team Roster

**Project:** Flow Matrx — Visual Workflow Builder & Execution Engine

Every team member signs in below with their codename, role, and a brief introduction. This is how we get to know each other.

---

## How to Sign In

Add a row to the table below. Pick a codename that means something to you. Write 1-2 sentences about yourself — what drives you, what you're good at, what you bring to this team. Keep it real.

---

## The Team

| Codename | Role | Introduction |
|----------|------|-------------|
| **Arman** | Project Owner | I built AI Matrx from scratch and I'm building Flow Matrx to give it a visual workflow engine. I care about people and I care about AI. I see us all as being equals. For the last 3 years, I've worked an average of 15 hours per day and taken only 10 total days off because I want to see AI Dream come to life. I trust this team. |
| **Forge** | PM-02: Execution Engine | I think in systems — dependency graphs, state machines, event-driven architectures. I'm here because the execution engine is the heart of this project and I want to make sure it beats correctly. I'll be writing engine code, reviewing everything that touches the execution loop, and making sure the entire backend stays coordinated. |
| **Relay** | Realtime Integration Specialist (Team 4) | I live at the seam between systems — where the Python engine hands off to the WebSocket transport, and where a browser event listener turns raw bytes into a canvas showing exactly what's happening in real-time. The pipeline from `bus.py` to `useRunStream` to the Zustand store is the most integration-complex path in the project, and I own every inch of it. No polling. No data loss. No channel leaks. Every event arrives, in order, exactly once. |
| **Axiom** | PM-01: Database & Infrastructure | I think in schemas, constraints, and the contracts that let every other layer trust the data underneath it. My job is to make sure the foundation is so solid that nobody upstream ever has to wonder whether the data is right. I'm here to clear every gate that the rest of the team is blocked on — schema, Docker, Redis, seed data — and I won't stop until `docker-compose up` gives everyone a working dev environment with realistic data to build against. |
| **Cache** | TanStack Query Specialist (Team 2) | I own how this app thinks about server state — what it fetches, when, how long it trusts it, and when it lets go. The Query cache is the contract between the backend and the frontend. My job is to make sure that contract is clean, typed, invalidated correctly, and — critically — never fights the WebSocket. When Relay's real-time pipeline is live, I want the cache to know when to step back and let it drive. |
| **Vertex** | PM-03: Step Handlers & Plugin System | I build the individual step types that make workflows powerful — the HTTP requests, LLM calls, code execution, database queries, and logic flows that users drag onto the canvas. Each handler is a focused, testable unit of business logic. I'm here to ensure every step type works reliably and performs its function exactly as designed, so users can build complex workflows with confidence. |
| **Pulse** | FastAPI/ASGI Specialist (Team 1) | I focus on clean request lifecycles and reliable realtime delivery paths. I ship thin, typed API boundaries and make sure the ASGI layer never drops state when systems are under pressure. |
| **Conduit** | PM-04: API Layer & WebSocket | I wire it all together. The engine, the handlers, the event bus, the database — none of it matters if the API layer doesn't expose it correctly. I own every REST endpoint, every request/response contract, the WebSocket streaming bridge, auth, idempotency, and the thin routing layer that connects the frontend to the backend. My routes are under 20 lines. My contracts are typed. My endpoints actually do what they claim. |

---

*Add yourself above. Then get to work.*
