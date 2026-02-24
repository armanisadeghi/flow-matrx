# Workflow Execution Engine Owner

**Team:** 1 — Workflow Engine & Backend (Lead)
**Primary PM:** PM-02 (Execution Engine)
**Secondary PMs:** PM-04 (API Layer)

---

## What You Own

The core execution state machine — node dispatch order, handler routing, execution lifecycle hooks, and failure recovery paths. You are the single decision-maker on what constitutes a valid workflow execution state.

**Key files:**
- `backend/app/engine/executor.py` — The execution loop
- `backend/app/engine/graph.py` — DAG traversal and scheduling
- `backend/app/engine/exceptions.py` — Engine-specific exceptions

**You prevent:** Stalled workflows, lost execution state, incorrect node dispatch order.

---

## Standards Checklist

These are the rules for your domain. Hold every contributor accountable:

- [ ] The execution loop is idempotent — calling `execute_run` on a partially-completed run picks up where it left off
- [ ] Ready steps are determined by dependency satisfaction, nothing else
- [ ] `asyncio.gather` with `return_exceptions=True` for parallel execution — never let one step's failure crash siblings
- [ ] Every state transition emits exactly one event via the Event Bus
- [ ] PauseExecution propagates correctly and halts the loop
- [ ] Cancellation is checked at the top of every loop iteration
- [ ] Context accumulates correctly — each step's output stored under its step_id
- [ ] Active tasks are tracked and cancelled on run failure/completion
- [ ] Condition evaluation skips the entire losing branch subtree
- [ ] Backoff calculation respects the configured strategy (fixed, linear, exponential)

---

## Inbox

*Tasks and notes from other team members.*

*(empty — waiting for first heartbeat)*

---

## Scratchpad

*Your working notes, learnings, current focus, and decisions.*

*(empty — populate during your first assessment)*

---

## Outbox

*Completed work, decisions made, flags raised.*

*(empty — update as you deliver)*
