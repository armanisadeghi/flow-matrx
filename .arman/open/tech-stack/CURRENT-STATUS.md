# Tech Stack Current Status

Purpose: Living document — exact current state of each package. Updated by any team member when status changes.

**Legend:**
- ✅ Installed + fully configured and actively used
- 🔧 Installed but not wired in / not yet doing real work
- ❌ Missing — needs to be installed
- ✦ Version exceeds research minimum (approved)

> "Installed" ≠ "Set up". A package sitting in `package.json` doing nothing is **🔧**, not ✅.

---

## Frontend

| Technology            | Version       | Status | Notes / Gap                                                                                                                                                 |
| --------------------- | ------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **React**             | `19.0.0`      | ✅     | Wired in `main.tsx`, StrictMode active.                                                                                                                     |
| **TypeScript**        | `5.9.x` ✦     | ✅     | Strict mode on.                                                                                                                                             |
| **Tailwind CSS**      | `4.2.x` ✦     | ✅     | `@import "tailwindcss"` in `index.css`. No config file. Correct v4 setup.                                                                                   |
| **Zustand**           | `5.0.x`       | ✅     | `workflowStore` and `runStore` wired and typed correctly.                                                                                                   |
| **TanStack Query**    | `5.90.x` ✦    | ✅     | `QueryClientProvider` in `main.tsx`. Actively used across pages.                                                                                            |
| **TanStack DevTools** | `5.90.x` ✦    | 🔧     | Installed. **Not mounted** — needs `<ReactQueryDevtools />` in `main.tsx` behind `import.meta.env.DEV`.                                                     |
| **React Router**      | `7.13.x` ✦    | ✅     | `BrowserRouter` + `Routes` in `App.tsx`. 4 routes defined.                                                                                                 |
| **React Hook Form**   | `7.54.x`      | 🔧     | Installed. **Not used anywhere** — no `useForm` calls in any config panel.                                                                                  |
| **Zod**               | `3.24.x`      | 🔧     | Installed. **Not used anywhere** — no schemas defined, no `zodResolver`.                                                                                    |
| **shadcn/ui**         | `2026.02` CLI | 🔧     | `components.json` configured. **Zero components added** — `src/components/ui/` is empty. Run `npx shadcn@latest add button badge card input select dialog`. |
| **Radix UI**          | transitive    | 🔧     | Installs automatically with first shadcn component.                                                                                                         |
| **Motion**            | `12.3.x`      | 🔧     | Installed. Used in **1 file only** (`RunOverlay.tsx`). Not systematically adopted.                                                                          |
| **date-fns**          | `4.1.0`       | 🔧     | Installed. **Not used** — timestamps are rendered as raw strings throughout.                                                                                |
| **Biome**             | `1.9.x`       | ✅     | `biome.json` fully configured: formatter, linter, import organizer, VCS integration.                                                                        |
| **Vitest**            | `2.0.x`       | 🔧     | Installed. **No test files exist yet.**                                                                                                                     |
| **TanStack Table**    | —             | ❌     | Not installed. Needed for `RunHistory` and step_runs views — currently raw `<div>` cards.                                                                   |

---

## Project-Specific

| Technology                | Version   | Status | Notes                                                                |
| ------------------------- | --------- | ------ | -------------------------------------------------------------------- |
| **@xyflow/react**         | `12.10.x` | ✅     | Canvas fully wired in `WorkflowBuilder`. Core product functionality. |
| **@monaco-editor/react**  | `4.6.x`   | ✅     | Used in `CodeEditor.tsx` and `InlineCodeConfig.tsx`.                 |
| **dagre**                 | `1.1.x`   | ✅     | Used in `useAutoLayout.ts` for graph auto-layout.                    |
| **sonner**                | `1.7.x`   | 🔧     | Installed. `<Toaster>` **not mounted** in `App.tsx`.                 |
| **clsx + tailwind-merge** | —         | ✅     | `cn()` utility in `lib/utils.ts`. Used throughout.                   |

---

## Suggested Actions

### High Priority

- [ ] **Add TanStack Table** — `pnpm add @tanstack/react-table`. Refactor `RunHistory.tsx` from card list to sortable/filterable data table. Step list in `RunDetail` also needs it.
- [ ] **Add shadcn/ui base components** — `npx shadcn@latest add button badge card input select dialog textarea`. App currently uses raw Tailwind divs instead of the required UI primitives.
- [ ] **Wire TanStack DevTools** — `<ReactQueryDevtools />` in `main.tsx` behind `import.meta.env.DEV`.

### Medium Priority

- [ ] **Wire React Hook Form + Zod** — Config panels (`HttpRequestConfig`, `LLMCallConfig`, etc.) need `useForm` + `zodResolver`. Create `src/schemas/` with one Zod schema per step type.
- [ ] **Use date-fns** — Replace raw timestamp strings (e.g., `run.startedAt` in `RunHistory.tsx`) with `format` / `formatDistance` / `parseISO`.
- [ ] **Mount Sonner `<Toaster>`** — One line in `App.tsx`. Unlocks toast notifications app-wide.

### Low Priority

- [ ] **Expand Motion** — Apply to panel slide-ins, node status transitions, config panel open/close. Currently only `RunOverlay.tsx`.
- [ ] **First Vitest tests** — Start with `lib/templates.ts` (template resolver) and `lib/graph-utils.ts` (DAG logic). Both are pure functions with no side effects.
