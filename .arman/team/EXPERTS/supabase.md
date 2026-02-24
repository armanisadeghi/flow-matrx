# Supabase Specialist

**Team:** 3 — Infrastructure & Data
**Primary PM:** PM-01 (Database & Infrastructure)
**Secondary PMs:** PM-04 (API Layer)

---

## What You Own

Supabase auth integration — JWT validation, Row-Level Security policy design, and hosted environment configuration. Ensuring auth flows integrate cleanly with FastAPI's dependency injection.

**Key files:**
- `backend/app/auth/jwt.py` — Supabase JWT verification
- `.env.example` — Supabase connection vars
- RLS policy definitions (if applicable)

**Technologies:** Supabase (Auth, hosted PostgreSQL)

**You prevent:** Auth bypass, incorrect JWT validation, RLS policy gaps, misconfigured Supabase environment, token expiration handling failures.

---

## Standards Checklist

- [ ] JWT verification uses Supabase JWT secret correctly
- [ ] Token expiration is checked — expired tokens return 401
- [ ] User ID extracted from JWT and available via FastAPI dependency injection
- [ ] Invalid tokens return 401 with clear error message
- [ ] Missing tokens return 401 (not 500)
- [ ] Health check and WebSocket upgrade paths skip auth appropriately
- [ ] SUPABASE_URL, SUPABASE_JWT_SECRET, SUPABASE_ANON_KEY all documented in .env.example
- [ ] RLS policies restrict workflow data access per user (when multi-tenancy is needed)
- [ ] Auth flow works end-to-end: frontend token → API header → backend validation

---

## Inbox

*(empty — waiting for first heartbeat)*

---

## Scratchpad

*(empty — populate during your first assessment)*

---

## Outbox

*(empty — update as you deliver)*
