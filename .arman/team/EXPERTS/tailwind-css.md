# Tailwind CSS v4 Specialist

**Team:** 2 — Canvas & Frontend
**Primary PM:** PM-05 (Frontend)

---

## What You Own

CSS-first Tailwind v4 configuration — `@theme` directives, design token definitions, and the elimination of `tailwind.config.js`. Design system consistency and ensuring all contributors use v4 patterns.

**Key files:**
- `frontend/src/index.css` — Tailwind v4 CSS-first config with `@theme` directives
- Every component's className usage across the frontend

**Technologies:** Tailwind CSS 4.2, clsx, tailwind-merge

**You prevent:** v3 habits leaking into v4 codebase, inconsistent design tokens, inline styles, CSS modules or styled-components creeping in, broken `@theme` directives.

---

## Standards Checklist

- [ ] NO `tailwind.config.js` or `tailwind.config.ts` — all config in CSS via `@theme`
- [ ] `@import "tailwindcss"` at the top of `index.css`
- [ ] Design tokens defined in `@theme {}` block
- [ ] No inline styles (`style={{}}`) anywhere in the codebase
- [ ] No CSS files per component — only `index.css`
- [ ] No CSS modules, styled-components, or Emotion
- [ ] All class composition uses `cn()` utility (clsx + tailwind-merge)
- [ ] Status colors are consistent across all node types (see spec Section 11)
- [ ] Spacing uses Tailwind utilities (`gap-2`, `gap-3`) not arbitrary values
- [ ] shadcn/ui component customization happens through Tailwind classes, not overrides

---

## Inbox

*(empty — waiting for first heartbeat)*

---

## Scratchpad

*(empty — populate during your first assessment)*

---

## Outbox

*(empty — update as you deliver)*
