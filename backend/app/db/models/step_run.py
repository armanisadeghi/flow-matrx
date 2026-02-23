"""
StepRun Matrx-ORM model.

Generated from schema via Matrx-ORM reverse migration tooling.
Schema source: migrations/001_core_tables.sql
"""
from __future__ import annotations

# Matrx-ORM model definition
# Run: matrx-orm reverse --table step_runs  to regenerate from live schema


class StepRun:
    """
    ORM model for the `step_runs` table.

    Columns:
        id           UUID  PK DEFAULT gen_random_uuid()
        run_id       UUID  NOT NULL REFERENCES runs(id) ON DELETE CASCADE
        step_id      TEXT  NOT NULL  (matches node id in workflow definition JSONB)
        step_type    TEXT  NOT NULL  (denormalized from node definition)
        status       TEXT  NOT NULL DEFAULT 'pending'
                          CHECK ('pending','running','completed','failed',
                                 'skipped','waiting','cancelled')
        input        JSONB DEFAULT '{}'
        output       JSONB DEFAULT '{}'
        error        TEXT
        attempt      INT   NOT NULL DEFAULT 1
        started_at   TIMESTAMPTZ
        completed_at TIMESTAMPTZ
        created_at   TIMESTAMPTZ NOT NULL DEFAULT now()

    Unique: (run_id, step_id, attempt)
    """

    __tablename__ = "step_runs"

    id: str  # UUID
    run_id: str  # UUID FK → runs.id
    step_id: str
    step_type: str
    status: str  # 'pending' | 'running' | 'completed' | 'failed' | 'skipped' | 'waiting' | 'cancelled'
    input: dict
    output: dict
    error: str | None
    attempt: int
    started_at: str | None  # TIMESTAMPTZ ISO string
    completed_at: str | None  # TIMESTAMPTZ ISO string
    created_at: str  # TIMESTAMPTZ ISO string
