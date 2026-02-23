"""
Workflow Matrx-ORM model.

Generated from schema via Matrx-ORM reverse migration tooling.
Schema source: migrations/001_core_tables.sql
"""
from __future__ import annotations

# Matrx-ORM model definition
# Run: matrx-orm reverse --table workflows  to regenerate from live schema


class Workflow:
    """
    ORM model for the `workflows` table.

    Columns:
        id          UUID  PK DEFAULT gen_random_uuid()
        name        TEXT  NOT NULL
        description TEXT  DEFAULT ''
        version     INT   NOT NULL DEFAULT 1
        status      TEXT  NOT NULL DEFAULT 'draft'  CHECK ('draft','published','archived')
        definition  JSONB NOT NULL DEFAULT '{"nodes": [], "edges": []}'
        input_schema JSONB DEFAULT NULL
        created_by  UUID
        created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
        updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
    """

    __tablename__ = "workflows"

    # Fields are declared as class-level annotations for Matrx-ORM introspection.
    # Do NOT instantiate this as a dataclass — use the auto-generated ModelManager.

    id: str  # UUID
    name: str
    description: str
    version: int
    status: str  # 'draft' | 'published' | 'archived'
    definition: dict
    input_schema: dict | None
    created_by: str | None  # UUID
    created_at: str  # TIMESTAMPTZ ISO string
    updated_at: str  # TIMESTAMPTZ ISO string
