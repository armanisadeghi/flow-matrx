# Async Task Queue Specialist

**Team:** 1 — Workflow Engine & Backend
**Primary PM:** PM-02 (Execution Engine)
**Secondary PMs:** PM-01 (Database & Infrastructure)

---

## What You Own

arq worker design end-to-end — job registration, serialization contracts, retry policy, dead-letter behavior, and Redis queue backing configuration. Anything that runs outside the request/response cycle.

**Key files:**
- ARQ worker configuration and job definitions
- Redis connection configuration for task queue
- Background task integration in `backend/app/engine/executor.py`

**Technologies:** arq 0.27, Redis 8, asyncio

**You prevent:** Silent job drops, retry storms, arq worker desync from Redis queue, zombie tasks.

---

## Standards Checklist

- [ ] Every background job has explicit timeout configuration
- [ ] Retry policy is explicit per job type — no implicit infinite retries
- [ ] Job serialization uses JSON-safe types only — no pickle, no arbitrary objects
- [ ] Dead-letter behavior is defined — failed jobs are logged and queryable
- [ ] Worker pool sizing is documented and justified
- [ ] Redis connection for ARQ is separate from pub/sub connections if needed
- [ ] Worker graceful shutdown cancels in-progress tasks cleanly
- [ ] Job execution is idempotent — safe to re-run on failure
- [ ] `execute_run` works as both a direct coroutine and an ARQ task

---

## Inbox

*(empty — waiting for first heartbeat)*

---

## Scratchpad

*(empty — populate during your first assessment)*

---

## Outbox

*(empty — update as you deliver)*
