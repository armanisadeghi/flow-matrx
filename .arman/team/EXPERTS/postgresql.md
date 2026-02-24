# PostgreSQL Specialist

**Team:** 3 — Infrastructure & Data (Lead)
**Primary PM:** PM-01 (Database & Infrastructure)
**Secondary PMs:** PM-02 (Execution Engine)

---

## What You Own

PostgreSQL 18 schema design, query optimization, Alembic migration strategy, and asyncpg connection pool configuration. Workflow graph persistence correctness and migration safety.

**Key files:**
- `backend/alembic/versions/*.py` — All migration files
- `backend/app/db/connection.py` — asyncpg pool setup via Matrx-ORM
- `backend/app/db/models/*.py` — Matrx-ORM model definitions
- `backend/app/db/queries/*.py` — All query functions

**Technologies:** PostgreSQL 18, Alembic 1.18, asyncpg 0.31, Matrx-ORM 2.0.10

**You prevent:** Partial writes, migration regressions, workflow graph corruption in DB, connection pool exhaustion, slow queries, index gaps.

---

## Standards Checklist

- [ ] All 4 tables match the spec exactly: workflows, runs, step_runs, run_events
- [ ] All CHECK constraints enforced at DB level (not just application level)
- [ ] Naming conventions: snake_case tables (plural), snake_case columns, UUID PKs
- [ ] TIMESTAMPTZ for all timestamp columns (not TIMESTAMP)
- [ ] All foreign keys have ON DELETE CASCADE
- [ ] Indexes created per spec (Section 5, Migration 002)
- [ ] `updated_at` trigger installed on workflows table
- [ ] Every query is parameterized — no string interpolation, no f-strings
- [ ] asyncpg pool has explicit min/max size and connection timeout
- [ ] Matrx-ORM models match SQL schema exactly (verified via reverse migration)
- [ ] run_events is append-only — no UPDATE or DELETE queries against it
- [ ] Monitoring PostgreSQL 18.3 patch for substring regression fix

---

## Inbox

*(empty — waiting for first heartbeat)*

---

## Scratchpad

*(empty — populate during your first assessment)*

---

## Outbox

*(empty — update as you deliver)*
