"""
Run Matrx-ORM model.

Generated from schema via Matrx-ORM reverse migration tooling.
Schema source: migrations/001_core_tables.sql
"""
from __future__ import annotations

# Matrx-ORM model definition
# Run: matrx-orm reverse --table runs  to regenerate from live schema


class Run:
    """
    ORM model for the `runs` table.

    Columns:
        id               UUID  PK DEFAULT gen_random_uuid()
        workflow_id      UUID  NOT NULL REFERENCES workflows(id) ON DELETE CASCADE
        status           TEXT  NOT NULL DEFAULT 'pending'
                              CHECK ('pending','running','paused','completed','failed','cancelled')
        trigger_type     TEXT  NOT NULL DEFAULT 'manual'
                              CHECK ('manual','schedule','webhook','event')
        input            JSONB NOT NULL DEFAULT '{}'
        context          JSONB NOT NULL DEFAULT '{}'
        error            TEXT
        idempotency_key  TEXT  UNIQUE
        started_at       TIMESTAMPTZ
        completed_at     TIMESTAMPTZ
        created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
    """

    __tablename__ = "runs"

    id: str  # UUID
    workflow_id: str  # UUID FK → workflows.id
    status: str  # 'pending' | 'running' | 'paused' | 'completed' | 'failed' | 'cancelled'
    trigger_type: str  # 'manual' | 'schedule' | 'webhook' | 'event'
    input: dict
    context: dict
    error: str | None
    idempotency_key: str | None
    started_at: str | None  # TIMESTAMPTZ ISO string
    completed_at: str | None  # TIMESTAMPTZ ISO string
    created_at: str  # TIMESTAMPTZ ISO string
