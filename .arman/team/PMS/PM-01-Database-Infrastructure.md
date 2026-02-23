# PM-01: Database & Infrastructure

**Role:** Database & Infrastructure Project Manager
**Scope:** Schema, migrations, Docker, Redis, Supabase Auth, deployment config, seed data

---

## Mission

Own the data layer and infrastructure foundation that everything else depends on. The backend cannot write queries until the schema exists. The frontend cannot develop against real data until seed workflows exist. This track unblocks every other team.

---

## Big Goals

1. **Rock-solid PostgreSQL schema** that matches the spec exactly — naming conventions, constraints, indexes, triggers
2. **Reproducible local dev environment** via Docker Compose with all services healthy
3. **Supabase Auth integration** so the API can verify JWTs from the frontend
4. **Redis setup** for background task queue and pub/sub
5. **Seed data** that gives frontend and backend developers realistic workflows to build against
6. **Production-ready deployment config** for all infrastructure components

---

## Deliverables (Ordered by Priority)

### D1: Supabase Project Setup
- Create the Supabase project
- Configure the PostgreSQL instance
- Note connection strings, JWT secret, and anon key
- Document in .env.example

### D2: Database Schema — Migration 001 (Core Tables)
Write and apply the Alembic migration for all 4 tables:

**workflows**
- `id UUID PRIMARY KEY DEFAULT gen_random_uuid()`
- `name TEXT NOT NULL`
- `description TEXT DEFAULT ''`
- `version INT NOT NULL DEFAULT 1`
- `status TEXT NOT NULL DEFAULT 'draft'` with CHECK constraint: draft, published, archived
- `definition JSONB NOT NULL DEFAULT '{"nodes": [], "edges": []}'`
- `input_schema JSONB DEFAULT NULL`
- `created_by UUID`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`
- `updated_at TIMESTAMPTZ NOT NULL DEFAULT now()`
- `UNIQUE(name, version)`

**runs**
- `id UUID PRIMARY KEY DEFAULT gen_random_uuid()`
- `workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE`
- `status TEXT NOT NULL DEFAULT 'pending'` with CHECK: pending, running, paused, completed, failed, cancelled
- `trigger_type TEXT NOT NULL DEFAULT 'manual'` with CHECK: manual, schedule, webhook, event
- `input JSONB NOT NULL DEFAULT '{}'`
- `context JSONB NOT NULL DEFAULT '{}'`
- `error TEXT`
- `idempotency_key TEXT UNIQUE`
- `started_at TIMESTAMPTZ`
- `completed_at TIMESTAMPTZ`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`

**step_runs**
- `id UUID PRIMARY KEY DEFAULT gen_random_uuid()`
- `run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE`
- `step_id TEXT NOT NULL`
- `step_type TEXT NOT NULL`
- `status TEXT NOT NULL DEFAULT 'pending'` with CHECK: pending, running, completed, failed, skipped, waiting, cancelled
- `input JSONB DEFAULT '{}'`
- `output JSONB DEFAULT '{}'`
- `error TEXT`
- `attempt INT NOT NULL DEFAULT 1`
- `started_at TIMESTAMPTZ`
- `completed_at TIMESTAMPTZ`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`
- `UNIQUE(run_id, step_id, attempt)`

**run_events**
- `id UUID PRIMARY KEY DEFAULT gen_random_uuid()`
- `run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE`
- `step_id TEXT` (NULL for run-level events)
- `event_type TEXT NOT NULL`
- `payload JSONB NOT NULL DEFAULT '{}'`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`

### D3: Database Schema — Migration 002 (Indexes)
```sql
CREATE INDEX idx_runs_workflow_id ON runs(workflow_id);
CREATE INDEX idx_runs_status ON runs(status);
CREATE INDEX idx_runs_created_at ON runs(created_at DESC);
CREATE INDEX idx_runs_idempotency_key ON runs(idempotency_key) WHERE idempotency_key IS NOT NULL;
CREATE INDEX idx_step_runs_run_id ON step_runs(run_id);
CREATE INDEX idx_step_runs_status ON step_runs(status);
CREATE INDEX idx_step_runs_run_step ON step_runs(run_id, step_id);
CREATE INDEX idx_run_events_run_id ON run_events(run_id);
CREATE INDEX idx_run_events_created_at ON run_events(run_id, created_at);
CREATE INDEX idx_workflows_status ON workflows(status);
CREATE INDEX idx_workflows_name ON workflows(name);
```

### D4: Database Schema — Migration 003 (updated_at Trigger)
```sql
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
```

### D5: Matrx-ORM Model Generation
- After migrations are applied, run Matrx-ORM reverse migration tooling to generate model classes
- Verify generated models in `backend/app/db/models/` match the SQL schema exactly
- Models: Workflow, Run, StepRun, RunEvent

### D6: Docker Compose — Local Dev Environment
Update `docker-compose.yml` to match the spec:
- **PostgreSQL 18** (currently 16 — needs upgrade)
- **Redis 8** (currently 7 — needs upgrade)
- Backend: `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- Frontend: `pnpm dev --host`
- Health checks on Postgres and Redis
- Volume persistence for Postgres data

### D7: Redis Setup
- Configure Redis instance for ARQ background task queue
- Verify connectivity from backend container
- Document REDIS_URL in .env.example

### D8: Supabase Auth Configuration
- Configure Supabase Auth with JWT verification
- Implement JWT verification middleware for FastAPI (`backend/app/auth/jwt.py`)
- Extract user info from Supabase JWT tokens
- Set up SUPABASE_JWT_SECRET env var

### D9: Seed Data Script
Write `scripts/seed-workflow.py` that inserts 2-3 sample workflows:

1. **Linear workflow** (3 steps): HTTP Request -> Transform -> Send Email
2. **Parallel + Condition workflow** (5 steps): HTTP Request -> [LLM Call, Transform] -> Condition -> Send Email
3. **Approval workflow** (4 steps): HTTP Request -> Wait for Approval -> Inline Code -> Webhook

Each workflow must have:
- Valid React Flow node positions (spread out for visual clarity)
- Realistic config with template references
- Status = 'published' so they're immediately runnable

### D10: Environment Variable Documentation
Ensure `.env.example` contains all required variables:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/flow_matrx
REDIS_URL=redis://localhost:6379
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_JWT_SECRET=your-jwt-secret
CORS_ORIGINS=http://localhost:5173
LOG_LEVEL=info
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

### D11: Production Deployment Config
- Backend Dockerfile optimized for production (multi-stage build)
- Frontend Dockerfile for static SPA build
- Document deployment targets: Vercel (frontend), Coolify/Railway (backend), Supabase (Postgres), Upstash (Redis)

---

## Naming Conventions (Enforced)

- Table names: snake_case, plural (`workflows`, `runs`, `step_runs`)
- Column names: snake_case (`created_at`, `workflow_id`)
- Enum values: snake_case (`wait_for_approval`, `http_request`)
- Primary keys: always `id UUID DEFAULT gen_random_uuid()`
- Foreign keys: always `{table_singular}_id`
- Timestamps: always `TIMESTAMPTZ`, always include `created_at`

---

## Critical Rules

- **run_events is append-only.** Never update or delete events.
- **Workflow definitions are immutable once published.** Published rows cannot be edited.
- **step_runs.input stores RESOLVED config** (templates already filled in).
- **runs.context is the shared scratchpad** — the ONLY mechanism for passing data between steps.
- **Alembic handles DDL. Matrx-ORM handles runtime data access.** These are complementary.
- **Every DB query is parameterized.** No string interpolation, no f-strings in queries.

---

## Coordination Points

| Milestone | Who's Waiting | Gate |
|-----------|---------------|------|
| Schema migrated | PM-02 (Engine), PM-04 (API) | Cannot write DB queries until schema exists |
| Docker Compose working | All teams | Everyone needs local dev environment |
| Seed data inserted | PM-05 (Frontend) | Frontend needs data to develop against |
| Supabase Auth configured | PM-04 (API) | API auth middleware depends on JWT secret |
| Redis running | PM-02 (Engine) | Background task queue needs Redis |

---

## Success Criteria

- [ ] All 3 migrations applied cleanly to a fresh Postgres 18 instance
- [ ] Matrx-ORM models match SQL schema exactly
- [ ] `docker-compose up` brings up all services with health checks passing
- [ ] Seed script inserts 3 sample workflows that can be fetched via API
- [ ] JWT verification correctly validates Supabase tokens
- [ ] Redis accepts connections from backend for ARQ
- [ ] .env.example is complete and documented
