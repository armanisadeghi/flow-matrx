"""
RunEvent Matrx-ORM model.

Generated from schema via Matrx-ORM reverse migration tooling.
Schema source: migrations/001_core_tables.sql
"""
from __future__ import annotations

# Matrx-ORM model definition
# Run: matrx-orm reverse --table run_events  to regenerate from live schema


class RunEvent:
    """
    ORM model for the `run_events` table.

    Append-only log. The engine writes events here.
    The WebSocket reads from here. This is the single source of truth
    for what happened during a run.

    Columns:
        id          UUID  PK DEFAULT gen_random_uuid()
        run_id      UUID  NOT NULL REFERENCES runs(id) ON DELETE CASCADE
        step_id     TEXT  NULL  (NULL for run-level events)
        event_type  TEXT  NOT NULL
        payload     JSONB NOT NULL DEFAULT '{}'
        created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
    """

    __tablename__ = "run_events"

    id: str  # UUID
    run_id: str  # UUID FK → runs.id
    step_id: str | None  # NULL for run-level events (run.started, run.completed, etc.)
    event_type: str  # See EventType enum in events/types.py
    payload: dict
    created_at: str  # TIMESTAMPTZ ISO string
