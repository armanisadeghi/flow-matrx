# PM-02: Execution Engine

**Role:** Execution Engine Project Manager
**Scope:** Core engine loop, graph utilities, template resolution, workflow validation, event bus, engine exceptions

---

## Mission

Build the heart of the system — the execution engine that walks a workflow DAG, runs steps in parallel, handles conditions/retries/pauses, and broadcasts events at every state transition. This is the most critical code in the entire project. Every real-time feature depends on the engine emitting events correctly.

---

## Big Goals

1. **Correct execution loop** — parallel execution, dependency resolution, condition branching, retry logic, pause/resume, cancellation
2. **Event Bus** — in-process pub/sub that persists events AND broadcasts to WebSocket subscribers
3. **Template Resolution** — Jinja2-based system that resolves `{{context.step_id.field}}` references
4. **Graph Helper** — pure-logic DAG traversal (dependencies, ready steps, branch detection)
5. **Workflow Validation** — DAG cycle detection, template reference checking, node type verification
6. **Idempotent resume** — calling execute_run on a partially-completed run picks up where it left off

---

## Deliverables (Ordered by Priority)

### D1: Engine Exceptions
**File:** `backend/app/engine/exceptions.py`

Define custom exception classes:
- `PauseExecution(step_id: str, reason: str)` — raised by approval/wait steps to pause the run
- `StepTimeout(message: str)` — raised when a step exceeds its timeout
- `EngineError(message: str)` — base class for engine-specific errors

### D2: Event Bus (MUST BE BUILT BEFORE THE ENGINE)
**File:** `backend/app/events/bus.py`

The Event Bus is the communication backbone. It:
1. Persists every event to the `run_events` table
2. Pushes events to all active WebSocket subscribers for a run_id

Key implementation:
- `emit(run_id, event_type, step_id=None, payload=None)` — persist + broadcast
- `subscribe(run_id) -> asyncio.Queue` — register a WebSocket listener
- `unsubscribe(run_id, queue)` — deregister
- Subscribers stored as `dict[str, list[asyncio.Queue]]`

### D3: Event Types
**File:** `backend/app/events/types.py`

Define the EventType enum with ALL event types:
```python
class EventType(str, Enum):
    RUN_STARTED     = "run.started"
    RUN_COMPLETED   = "run.completed"
    RUN_FAILED      = "run.failed"
    RUN_PAUSED      = "run.paused"
    RUN_RESUMED     = "run.resumed"
    RUN_CANCELLED   = "run.cancelled"
    STEP_STARTED    = "step.started"
    STEP_COMPLETED  = "step.completed"
    STEP_FAILED     = "step.failed"
    STEP_SKIPPED    = "step.skipped"
    STEP_WAITING    = "step.waiting"
    STEP_RETRYING   = "step.retrying"
    CONTEXT_UPDATED = "context.updated"
```

Each event type has a defined payload shape. These payloads are documented in the spec (Section 6) and are NOT negotiable — the frontend depends on them.

### D4: Graph Helper
**File:** `backend/app/engine/graph.py`

Pure logic class — no I/O, no database, no side effects:
- `__init__(nodes, edges)` — build adjacency structures (dependencies, children, root_ids)
- `get_ready_steps(done_ids) -> list[dict]` — return nodes with all deps satisfied. THIS IS THE SCHEDULING ALGORITHM.
- `get_branch_nodes(condition_id, branch_label) -> set[str]` — all downstream nodes on a branch (for skipping the losing branch)
- `_all_descendants(node_id) -> set[str]` — recursive downstream collection
- `get_upstream_ids(node_id) -> set[str]` — all ancestor node IDs (for template reference validation)

### D5: Template Resolution
**File:** `backend/app/engine/templates.py`

Resolve `{{template}}` strings in any data structure:
- `resolve_templates(obj, scope) -> Any` — recursively resolve templates in strings, dicts, lists
- If entire string is one template (`{{step_1.users}}`), return the actual value (preserving type — could be dict, list, int)
- If string contains interpolation (`Hello {{step_1.name}}`), render as Jinja2 string
- Support Jinja2 filters (`{{step_1.items | length}}`) and loops (`{% for item in ... %}`)
- Use `StrictUndefined` — raise error on missing keys, never silently produce empty string
- `_deep_get(data, path)` — navigate nested dicts/lists by dot path (`step_1.users.0.name`)
- `extract_template_refs(obj) -> set[str]` — find all `{{...}}` references (for validation)

### D6: Safe Expression Evaluation
**File:** `backend/app/engine/safe_eval.py`

For condition node evaluation:
- Evaluate simple expressions in a sandboxed environment
- No imports, no file access, no network
- Support basic comparisons, boolean logic, string operations
- Input is a resolved template string, output is a truthy/falsy value

### D7: Workflow Validation
**File:** `backend/app/validation/workflow.py`

`validate_workflow(definition) -> list[str]` returns error messages (empty = valid):
1. Must have at least one node
2. All edge endpoints must reference existing nodes
3. Cycle detection (topological sort — workflow must be a DAG)
4. All node types must be registered in STEP_REGISTRY
5. Condition nodes must have exactly one 'true' and one 'false' outgoing edge
6. No orphan nodes in multi-node workflows
7. Template references must point to upstream steps (not downstream or siblings)

### D8: The Execution Engine (CORE)
**File:** `backend/app/engine/executor.py`

`WorkflowEngine` class with:

**`execute_run(run_id)`** — the main loop:
1. Load run + workflow from DB
2. Build Graph from definition
3. Initialize context from run input
4. Set run status to "running", emit `run.started`
5. LOOP:
   - Check for cancellation (re-fetch run status from DB)
   - Get completed + skipped step IDs from DB
   - Get ready steps from graph
   - If no ready steps: break (all done)
   - Execute ready steps in parallel via `asyncio.gather` with `return_exceptions=True`
   - Process results:
     - `PauseExecution` → update run to paused, emit `run.paused`, return
     - `Exception` with `on_error=skip` → mark step skipped, emit `step.skipped`, continue
     - `Exception` with `on_error=fail` → update run to failed, emit `run.failed`, return
     - Success → add output to context, update run context, emit `context.updated`
6. After loop: update run to completed, emit `run.completed`
7. On unexpected exception: update run to failed, emit `run.failed`
8. Finally: cancel any remaining asyncio tasks

**`_execute_step(run_id, node, context, graph)`** — single step execution:
1. Handle condition nodes specially (`_evaluate_condition`)
2. Handle wait_for_approval nodes (emit `step.waiting`, raise PauseExecution)
3. Resolve templates in config
4. Get handler from registry
5. Retry loop (1 to max_attempts):
   - Create step_run record (status=running)
   - Emit `step.started`
   - Execute handler with `asyncio.wait_for` (timeout support)
   - On success: validate output size, save to DB, emit `step.completed`, return result
   - On timeout/error: save failure to DB
   - If will_retry: emit `step.retrying`, sleep with backoff
   - If exhausted: emit `step.failed`, raise

**`_evaluate_condition(run_id, node, context, graph)`**:
1. Resolve condition expression from templates
2. Emit `step.started`
3. Evaluate via safe_eval
4. Save condition result to DB, emit `step.completed`
5. Determine losing branch
6. Mark all nodes on losing branch as skipped (emit `step.skipped` for each)
7. Return `{"result": bool_value}`

**Backoff calculation:**
- `fixed` — constant delay
- `linear` — base * attempt
- `exponential` — base ** attempt

**Output truncation for events:**
- `_truncate_for_display(output, max_keys=5)` — create small summary for WebSocket events (not full output)

### D9: Background Task Integration
- Integrate with ARQ for running workflows as background tasks
- `execute_run` should be callable as both a direct coroutine and an ARQ task
- Handle cleanup when the worker process dies mid-execution

---

## Mandatory Event Emission Points

The engine MUST call `event_bus.emit()` at every one of these moments. Missing ANY breaks the frontend:

| Moment | Event Type | Required Payload Fields |
|--------|-----------|------------------------|
| Run starts executing | `run.started` | status |
| Run finishes all steps | `run.completed` | status, duration_ms |
| Run fails | `run.failed` | status, error, failed_step_id (if applicable) |
| Run pauses for approval | `run.paused` | status, waiting_step_id, reason |
| Run resumes | `run.resumed` | status, resumed_step_id |
| Run cancelled | `run.cancelled` | status |
| Step begins | `step.started` | step_id, step_type, step_label, attempt |
| Step succeeds | `step.completed` | step_id, step_type, status, output_summary, duration_ms |
| Step fails (final) | `step.failed` | step_id, step_type, status, error, attempt |
| Step skipped (branch) | `step.skipped` | step_id, status, reason |
| Step waiting | `step.waiting` | step_id, step_type, status, waiting_for, label |
| Step retrying | `step.retrying` | step_id, attempt, max_attempts, backoff_seconds, error |
| Context updated | `context.updated` | step_id, keys_added |

---

## Dependencies

| Needs From | What | Blocking? |
|-----------|------|-----------|
| PM-01 | Schema migrated + Matrx-ORM models | YES — cannot write DB queries |
| PM-01 | Redis running | YES — needed for ARQ |
| PM-03 | Step handlers registered | NO — engine can use mock handlers for testing |

---

## What This Track Produces For Others

| Consumer | What They Get |
|----------|---------------|
| PM-04 (API) | WorkflowEngine class to call from endpoints |
| PM-04 (API) | Event Bus to wire into WebSocket endpoint |
| PM-04 (API) | Validation function to call from validate endpoint |
| PM-05 (Frontend) | Event format specification for WebSocket hook |

---

## Testing Requirements (90%+ Coverage)

### Engine Tests (`tests/test_engine/test_executor.py`)
- Linear workflow (A -> B -> C) executes in sequence
- Parallel branches (A -> [B, C] -> D) — B and C execute in parallel
- Condition true branch — true-branch executes, false-branch skipped
- Condition false branch — reverse
- Fan-in waits for all (D depends on B and C — D starts when BOTH complete)
- Step failure stops run (on_error=fail)
- Step failure skip continues (on_error=skip)
- Retry with eventual success (fail twice, succeed third)
- Retry exhausted fails
- Timeout triggers retry
- Pause and resume (wait_for_approval)
- Cancellation mid-execution
- Resume picks up correctly (skip completed steps)
- Context accumulates (each step output under its step_id)
- Template resolution in config

### Event Emission Tests (`tests/test_engine/test_events.py`)
One test per event type verifying:
- Correct event_type string
- Correct payload shape
- Event persisted to run_events table
- Event delivered to WebSocket subscriber queue

### Graph Tests
- Root node detection
- Ready step calculation with various DAG shapes
- Branch detection for conditions
- Upstream ID collection
- Cycle detection in validation

### Template Tests
- Simple variable substitution
- Type preservation (dict stays dict, list stays list)
- Jinja2 string interpolation
- Jinja2 filters
- Deep path navigation (dot notation)
- StrictUndefined raises on missing keys
- extract_template_refs finds all references

---

## Success Criteria

- [ ] Engine executes a linear 3-step workflow end-to-end
- [ ] Engine handles parallel branches correctly (asyncio.gather)
- [ ] Condition branching skips the losing branch's entire subtree
- [ ] Retry logic works with fixed, linear, and exponential backoff
- [ ] Pause/resume works for approval workflows
- [ ] Cancellation stops execution at next loop iteration
- [ ] Every state transition emits the correct event with correct payload
- [ ] Events are persisted to run_events table
- [ ] Events are delivered to WebSocket subscribers
- [ ] Template resolution handles all documented cases
- [ ] Workflow validation catches all 7 error categories
- [ ] 90%+ test coverage on engine code
