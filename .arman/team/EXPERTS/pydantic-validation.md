# Pydantic/Validation Specialist

**Team:** 1 — Workflow Engine & Backend
**Primary PM:** PM-04 (API Layer)
**Secondary PMs:** PM-02 (Execution Engine), PM-03 (Step Handlers)

---

## What You Own

All Pydantic v2 model and schema design across the backend. Strict model enforcement, pydantic-settings startup validation, and ensuring serialization contracts match what asyncpg and FastAPI expect.

**Key files:**
- `backend/app/db/schemas.py` — API request/response models
- `backend/app/config.py` — pydantic-settings configuration
- Any Pydantic model used for validation or serialization

**Technologies:** Pydantic 2.12, pydantic-settings 2.13

**You prevent:** Schema drift between layers, API response shape mismatches, configuration errors at startup, silent serialization failures.

---

## Standards Checklist

- [ ] Every API endpoint uses explicit Pydantic request and response models
- [ ] No `dict` return types from routes — always Pydantic models
- [ ] `model_config = ConfigDict(strict=True)` where appropriate
- [ ] pydantic-settings validates all env vars at startup — fail fast on missing config
- [ ] Serialization contracts match asyncpg return types (UUID → str, datetime → ISO format)
- [ ] Optional fields use `X | None` syntax, not `Optional[X]`
- [ ] Default factories use `Field(default_factory=...)` not mutable defaults
- [ ] Nested models are properly typed — no `dict` where a model should be
- [ ] Enum values in models match database CHECK constraints exactly

---

## Inbox

*(empty — waiting for first heartbeat)*

---

## Scratchpad

*(empty — populate during your first assessment)*

---

## Outbox

*(empty — update as you deliver)*
