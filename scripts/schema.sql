-- ============================================================
-- Flow Matrx — Final Database Schema
-- Version: 2.0  |  Date: 2026-03-01
-- ============================================================
--
-- 4 core tables, no more, no less.
-- This schema matches the engine, API, and frontend contracts.
--
-- IMPORTANT: Run these in order. Indexes and triggers at the end.
-- ============================================================


-- ============================================================
-- TABLE 1: workflows
-- ============================================================
-- Workflow definitions. Immutable once published.
-- The `definition` JSONB column stores the React Flow graph verbatim.
-- Versioning: publishing freezes the row. Editing creates a new version.

CREATE TABLE workflows (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    description     TEXT NOT NULL DEFAULT '',
    version         INT NOT NULL DEFAULT 1,
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK (status IN ('draft', 'published', 'archived')),

    -- The React Flow graph. Stored verbatim, never translated.
    -- Shape: {
    --   "nodes": [
    --     {
    --       "id": "step_1",
    --       "type": "http_request",              -- step handler type
    --       "position": {"x": 100, "y": 200},    -- canvas position
    --       "data": {
    --         "label": "Fetch Users",             -- display name
    --         "config": { ... },                  -- handler-specific config
    --         "on_error": "fail",                 -- "fail" | "skip" | "continue"
    --         "max_attempts": 1,                  -- retry count
    --         "backoff_strategy": "fixed",        -- "fixed" | "linear" | "exponential"
    --         "backoff_base": 2.0,                -- seconds
    --         "timeout_seconds": null             -- per-step timeout (null = none)
    --       }
    --     }
    --   ],
    --   "edges": [
    --     {
    --       "id": "e1",
    --       "source": "step_1",
    --       "target": "step_2",
    --       "sourceHandle": null,                 -- "true"/"false" for conditions
    --       "data": {
    --         "condition": null                   -- alt: edge-level branch label
    --       }
    --     }
    --   ]
    -- }
    definition      JSONB NOT NULL DEFAULT '{"nodes": [], "edges": []}',

    -- Optional JSON Schema for run inputs.
    -- Frontend renders an input form from this before starting a run.
    input_schema    JSONB DEFAULT NULL,

    -- Who created this workflow (Supabase Auth user ID).
    -- NULL for system-generated or imported workflows.
    created_by      UUID,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- A workflow name + version must be unique.
    UNIQUE(name, version)
);


-- ============================================================
-- TABLE 2: runs
-- ============================================================
-- A single execution of a workflow.
-- The engine reads the workflow definition, walks the graph, and
-- accumulates results in `context`.

CREATE TABLE runs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id     UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,

    status          TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN (
                        'pending',      -- created, not yet started
                        'running',      -- engine is actively executing
                        'paused',       -- waiting for human approval or external event
                        'completed',    -- all steps done successfully
                        'failed',       -- a step failed with on_error=fail
                        'cancelled'     -- manually cancelled via API
                    )),

    trigger_type    TEXT NOT NULL DEFAULT 'manual'
                    CHECK (trigger_type IN ('manual', 'schedule', 'webhook', 'event')),

    -- User-provided input for this run (e.g. form data).
    -- Accessible in templates as {{input.field_name}}.
    input           JSONB NOT NULL DEFAULT '{}',

    -- Shared scratchpad. Accumulated by the engine after each step.
    -- Shape: {
    --   "input": { ... },          -- copied from runs.input
    --   "step_1": { ... output },  -- step_1's handler return value
    --   "step_2": { ... output },  -- step_2's handler return value
    -- }
    -- Steps reference upstream data via {{step_id.field}} templates.
    -- This is the ONLY mechanism for passing data between steps.
    context         JSONB NOT NULL DEFAULT '{}',

    -- Error message if status = 'failed'. NULL otherwise.
    error           TEXT,

    -- Prevents duplicate runs from retries or double-clicks.
    -- POST /api/v1/workflows/{id}/run with X-Idempotency-Key header.
    idempotency_key TEXT UNIQUE,

    -- Who triggered this run (Supabase Auth user ID).
    -- NULL for schedule/webhook/event triggers.
    created_by      UUID,

    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);


-- ============================================================
-- TABLE 3: step_runs
-- ============================================================
-- Individual step execution records within a run.
-- One row per (step, attempt). Retries create new rows with attempt+1.

CREATE TABLE step_runs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id          UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,

    -- Matches the node "id" in the workflow definition JSONB.
    -- NOT a foreign key — references the graph, not another table.
    step_id         TEXT NOT NULL,

    -- Denormalized from the node definition for query convenience.
    -- Values: http_request, llm_call, inline_code, condition,
    --         database_query, transform, delay, wait_for_approval,
    --         wait_for_event, send_email, webhook, for_each,
    --         function_call
    step_type       TEXT NOT NULL,

    status          TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN (
                        'pending',      -- not yet started
                        'running',      -- currently executing
                        'completed',    -- finished successfully
                        'failed',       -- threw an error
                        'skipped',      -- on the losing branch of a condition
                        'waiting',      -- paused for approval or external event
                        'cancelled'     -- run was cancelled while this was pending/running
                    )),

    -- The RESOLVED config passed to the handler (templates filled in).
    -- Critical for debugging — shows exactly what the step received.
    input           JSONB DEFAULT '{}',

    -- The return value from the handler.
    output          JSONB DEFAULT '{}',

    -- Error message if status = 'failed'. NULL otherwise.
    error           TEXT,

    -- Retry attempt number. Starts at 1.
    attempt         INT NOT NULL DEFAULT 1,

    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- A step can have multiple attempts (retries), but each attempt
    -- is a unique row. Only ONE should be in a non-failed state.
    UNIQUE(run_id, step_id, attempt)
);


-- ============================================================
-- TABLE 4: run_events
-- ============================================================
-- Append-only event log. Source of truth for audit, replay, WebSocket.
-- The engine writes events here. The WebSocket reads from here.
-- NEVER update or delete rows in this table.

CREATE TABLE run_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id          UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,

    -- NULL for run-level events (run.started, run.completed, etc.)
    -- Set to node "id" for step-level events.
    step_id         TEXT,

    -- Event types (13 total):
    --   Run-level:  run.started, run.completed, run.failed,
    --               run.paused, run.resumed, run.cancelled
    --   Step-level: step.started, step.completed, step.failed,
    --               step.skipped, step.waiting, step.retrying
    --   Context:    context.updated
    event_type      TEXT NOT NULL,

    -- Event-specific data. Shape varies by event_type.
    -- All payloads include at minimum {"status": "..."}.
    -- step.completed includes {"output_summary": {...}, "duration_ms": int}
    -- run.paused includes {"waiting_step_id": "...", "reason": "..."}
    payload         JSONB NOT NULL DEFAULT '{}',

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);


-- ============================================================
-- INDEXES
-- ============================================================

-- workflows
CREATE INDEX idx_workflows_status ON workflows(status);
CREATE INDEX idx_workflows_name ON workflows(name);
CREATE INDEX idx_workflows_created_by ON workflows(created_by) WHERE created_by IS NOT NULL;

-- runs
CREATE INDEX idx_runs_workflow_id ON runs(workflow_id);
CREATE INDEX idx_runs_status ON runs(status);
CREATE INDEX idx_runs_created_at ON runs(created_at DESC);
CREATE INDEX idx_runs_created_by ON runs(created_by) WHERE created_by IS NOT NULL;
CREATE INDEX idx_runs_idempotency_key ON runs(idempotency_key)
    WHERE idempotency_key IS NOT NULL;

-- step_runs
CREATE INDEX idx_step_runs_run_id ON step_runs(run_id);
CREATE INDEX idx_step_runs_status ON step_runs(status);
CREATE INDEX idx_step_runs_run_step ON step_runs(run_id, step_id);

-- run_events (optimized for WebSocket replay and audit queries)
CREATE INDEX idx_run_events_run_id ON run_events(run_id);
CREATE INDEX idx_run_events_run_created ON run_events(run_id, created_at);
CREATE INDEX idx_run_events_type ON run_events(event_type);


-- ============================================================
-- TRIGGERS
-- ============================================================

-- Auto-update updated_at on workflows
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
