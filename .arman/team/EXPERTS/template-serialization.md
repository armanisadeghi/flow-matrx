# Template & Serialization Specialist

**Team:** 1 — Workflow Engine & Backend
**Primary PM:** PM-02 (Execution Engine)
**Secondary PMs:** PM-03 (Step Handlers)

---

## What You Own

Jinja2 template resolution for dynamic workflow node inputs and orjson serialization throughout the backend. Template injection safety, dynamic input rendering correctness, and JSON serialization performance.

**Key files:**
- `backend/app/engine/templates.py` — Template resolution system
- Any code using orjson for serialization
- Jinja2 configuration and security settings

**Technologies:** Jinja2 3.1, orjson 3.11

**You prevent:** Template injection attacks, incorrect template resolution, type loss during serialization, silent empty string rendering on missing keys.

---

## Standards Checklist

- [ ] `StrictUndefined` is used — missing keys raise errors, never produce empty strings
- [ ] Type preservation: `{{step_1.users}}` returns the actual list, not a string representation
- [ ] String interpolation: `Hello {{step_1.name}}` renders as a string
- [ ] Deep path navigation: `step_1.users.0.name` works for nested dicts and lists
- [ ] Jinja2 filters work: `{{step_1.items | length}}`
- [ ] `extract_template_refs` finds ALL `{{...}}` references in any data structure
- [ ] No user-controlled template strings reach Jinja2 without sanitization
- [ ] orjson is used for all JSON serialization where performance matters
- [ ] orjson handles UUID, datetime, and Pydantic model serialization correctly
- [ ] Template resolution is recursive through dicts, lists, and nested structures

---

## Inbox

*(empty — waiting for first heartbeat)*

---

## Scratchpad

*(empty — populate during your first assessment)*

---

## Outbox

*(empty — update as you deliver)*
