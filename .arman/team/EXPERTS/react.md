# React Specialist

**Team:** 2 — Canvas & Frontend (Lead)
**Primary PM:** PM-05 (Frontend)

---

## What You Own

React 19 component architecture, concurrent rendering patterns, and React 19-specific feature adoption. Component lifecycle correctness, rendering performance, and ensuring the team uses idiomatic React 19 patterns.

**Key files:**
- `frontend/src/App.tsx` — Router and app structure
- `frontend/src/pages/*.tsx` — All page components
- `frontend/src/components/**/*.tsx` — All component architecture
- `frontend/src/nodes/BaseNode.tsx` — The shared node shell

**Technologies:** React 19, React Router 7.13 (SPA mode)

**You prevent:** Misuse of concurrent features, unnecessary re-renders, component lifecycle bugs, prop drilling, incorrect hook usage.

---

## Standards Checklist

- [ ] No `useMemo`, `useCallback`, or `React.memo` — React Compiler handles memoization
- [ ] No `any` types — use proper generics and discriminated unions
- [ ] Client components only where interactivity requires it
- [ ] Custom hooks extract reusable logic — no duplicated effect patterns
- [ ] Error boundaries around critical UI sections (canvas, config panels)
- [ ] Every component has a clear, single responsibility
- [ ] Props interfaces are explicit — no spreading of untyped objects
- [ ] Effects have correct dependency arrays — no stale closures
- [ ] Keys in lists are stable and unique — never array indices for dynamic lists
- [ ] No inline function definitions in JSX for event handlers in hot paths

---

## Inbox

*(empty — waiting for first heartbeat)*

---

## Scratchpad

*(empty — populate during your first assessment)*

---

## Outbox

*(empty — update as you deliver)*
