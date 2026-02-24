# PM-05: Frontend — Canvas, Nodes, Panels & Live Execution

**Role:** Frontend Project Manager
**Scope:** React + Vite SPA, React Flow canvas, node components, config panels, Zustand stores, API client, WebSocket hook, run viewer, all pages

---

## Mission

Build the visual workflow builder and live execution viewer. Users drag steps from a palette onto a canvas, configure them via side panels, save/publish workflows, then watch them execute in real-time with every node animating through its status. This is the product surface — everything the user sees and touches.

---

## Big Goals

1. **React Flow Canvas** — drag-and-drop workflow builder with snapping, minimap, controls
2. **Step Palette** — draggable step types organized by category
3. **Node Components** — one per step type, extending BaseNode with status visualization
4. **Config Panels** — one per step type, using Zod + React Hook Form for validation
5. **Live Run Viewer** — WebSocket-powered real-time status overlay on canvas nodes
6. **4 Pages** — Workflow List, Workflow Builder, Run History, Run Detail
7. **State Management** — Zustand for client state, TanStack Query for server state
8. **Desktop-first tool** — minimum 1280px width, no mobile layouts

---

## Deliverables (Ordered by Priority)

### D1: Project Scaffold
- Vite 7.3 + React 19 + TypeScript 5.9 (strict mode)
- Tailwind CSS 4.2 with CSS-first config (NO tailwind.config.js)
- shadcn/ui initialized (`pnpm dlx shadcn@latest init`, New York style, CSS variables)
- Biome 1.9 for linting/formatting
- React Router 7.13 (SPA mode)
- Core dependencies installed (see package.json)

### D2: CSS Entry Point (Tailwind v4)
**File:** `frontend/src/index.css`
```css
@import "tailwindcss";

@theme {
  --color-brand-50: #f0f9ff;
  --color-brand-500: #3b82f6;
  --color-brand-600: #2563eb;
  --font-sans: "Inter", system-ui, sans-serif;
}
```
No tailwind.config.js. No tailwind.config.ts. All config in CSS.

### D3: shadcn/ui Components
Add these via `pnpm dlx shadcn@latest add <component>`:
- button, input, select, dialog, dropdown-menu, tooltip, badge, separator
- label, textarea, switch, tabs, card, scroll-area
- Add more as needed — ALL UI primitives come from shadcn/ui

### D4: Router Setup
**File:** `frontend/src/App.tsx`

4 routes (React Router SPA mode):
- `/` — WorkflowList (dashboard)
- `/workflows/:id` — WorkflowBuilder (canvas)
- `/workflows/:id/runs` — RunHistory
- `/runs/:id` — RunDetail

### D5: API Client
**File:** `frontend/src/api/client.ts`

Base fetch wrapper with:
- Base URL from `VITE_API_URL`
- Auth token injection (Supabase JWT)
- JSON serialization/deserialization
- Error handling (throw on non-2xx)

### D6: API Hooks (TanStack Query)
**Files:** `frontend/src/api/workflows.ts`, `runs.ts`

Workflow hooks:
- `useWorkflows()` — list with pagination/filtering
- `useWorkflow(id)` — single workflow
- `useSaveWorkflow()` — mutation for PUT
- `useCreateWorkflow()` — mutation for POST
- `usePublishWorkflow()` — mutation for POST .../publish
- `useValidateWorkflow()` — mutation for POST .../validate
- `useDeleteWorkflow()` — mutation for DELETE

Run hooks:
- `useRuns(workflowId?)` — list with filtering
- `useRun(id)` — single run
- `useStepRuns(runId)` — step runs for a run
- `useRunEvents(runId)` — events for replay
- `useStartRun()` — mutation for POST .../run
- `useResumeRun()` — mutation
- `useCancelRun()` — mutation

### D7: Zustand Stores

**Workflow Store** (`frontend/src/stores/workflowStore.ts`):
- Canvas state (nodes, edges, selected node)
- Dirty state tracking (unsaved changes)

**Run Store** (`frontend/src/stores/runStore.ts`):
```typescript
interface RunStore {
  activeRunId: string | null;
  runStatus: string | null;
  stepStatuses: Record<string, StepStatus>;
  connected: boolean;
  setActiveRun, setRunStatus, setStepStatus, setSnapshot, setConnected, reset
}
```
- `setSnapshot(statuses)` — bulk-set from WebSocket snapshot
- `setStepStatus(stepId, payload)` — update single step from live event
- `setRunStatus(payload)` — update run-level status

### D8: WebSocket Hook (CRITICAL)
**File:** `frontend/src/hooks/useRunStream.ts`

```typescript
function useRunStream(runId: string | null): void
```

- Connect to `WS /ws/runs/{runId}` when runId is set
- Handle `snapshot` message → call `setSnapshot()`
- Handle `event` message → route to `setStepStatus()` or `setRunStatus()` based on event_type
- Track connection state via `setConnected()`
- Clean up on unmount or runId change
- NO polling. Events are the ONLY mechanism for live updates.

### D9: BaseNode Component
**File:** `frontend/src/nodes/BaseNode.tsx`

Shared node shell that all step nodes extend:
- Target handle (top) + Source handle (bottom)
- Header: icon + label
- Body: step-type-specific content (children)
- Status footer: shown during runs (duration, error, attempt info)
- Status-driven styling:

| Status | Border | Background | Animation |
|--------|--------|------------|-----------|
| pending | gray-200 | white | none |
| running | blue-400 | blue-50 | animate-pulse |
| completed | emerald-400 | emerald-50 | none |
| failed | red-400 | red-50 | none |
| skipped | gray-300 | gray-50 | opacity-50 |
| waiting | amber-400 | amber-50 | ring-2 ring-amber-200 |
| retrying | orange-400 | orange-50 | animate-pulse |

- Selected state: `ring-2 ring-blue-500`
- Min width: 220px
- Transitions: `transition-all duration-200`

### D10: Node Components (One Per Step Type)
**Files:** `frontend/src/nodes/`

Each node extends BaseNode with an icon and step-specific preview:

| Type | Icon | Preview Content |
|------|------|-----------------|
| HttpRequestNode | Globe | `{method} {url}` |
| LLMCallNode | Brain | `{provider}: {model}` |
| InlineCodeNode | Code | First line of code |
| ConditionNode | GitBranch | Expression preview |
| DatabaseQueryNode | Database | Query preview (truncated) |
| ApprovalNode | UserCheck | Label / instructions |
| DelayNode | Clock | `{seconds}s` |
| TransformNode | Shuffle | Output field names |
| SendEmailNode | Mail | `To: {recipient}` |
| WebhookNode | Webhook | URL preview |

Register all in `nodes/index.ts`:
```typescript
export const nodeTypes = {
  http_request: HttpRequestNode,
  llm_call: LLMCallNode,
  // ...all types
};
```

### D11: Config Panels (One Per Step Type)
**Files:** `frontend/src/config-panels/`

Each panel uses the Zod + React Hook Form pattern:
1. Define Zod schema
2. Derive TypeScript type via `z.infer`
3. Use `useForm` with `zodResolver`
4. All inputs use shadcn/ui components (Input, Select, Textarea, etc.)
5. Call `onChange` on every field change to update node data

**Panels needed:**
- HttpRequestConfig: method (select), url (input), headers (key-value editor), body (textarea)
- LLMCallConfig: provider (select), model (input), prompt (textarea), system_prompt (textarea), max_tokens (number), temperature (slider)
- InlineCodeConfig: code (Monaco editor)
- ConditionConfig: expression (TemplateInput)
- DatabaseQueryConfig: query (Monaco editor with SQL), params (key-value)
- ApprovalConfig: label (input), instructions (textarea)
- DelayConfig: seconds (number input)
- TransformConfig: output template (JSON editor)
- SendEmailConfig: to (TemplateInput), subject (TemplateInput), body (textarea), html toggle
- WebhookConfig: url (TemplateInput), payload (JSON editor), headers (key-value)

Register all in `config-panels/index.ts`.

### D12: NodeConfigPanel Container
**File:** `frontend/src/components/canvas/NodeConfigPanel.tsx`

- Receives selected node
- Looks up the correct config panel from the registry based on node type
- Passes config and onChange handler
- Shows upstream step IDs for template autocomplete context
- 320px wide, slides in from right on node selection

### D13: Step Palette
**File:** `frontend/src/components/canvas/StepPalette.tsx`

- Fetch step catalog from `GET /api/v1/catalog/steps`
- Group by category (integrations, ai, logic, data, flow)
- Each item is draggable (HTML5 drag-and-drop)
- On drop onto canvas: create new node at drop position with default config
- 200px wide, fixed left sidebar
- Icons from Lucide React (matching the catalog icon names)

### D14: Workflow Builder Page (THE MAIN PAGE)
**File:** `frontend/src/pages/WorkflowBuilder.tsx`

Layout:
```
[Palette 200px] [Canvas flex-1] [Config Panel 320px (conditional)]
```

- React Flow instance with: Background, Controls, MiniMap
- `nodeTypes` from registry
- `snapToGrid` with 16px grid
- `fitView` on load
- Node click → select → show config panel
- Pane click → deselect → hide config panel
- Connection → addEdge
- Save button → serialize nodes + edges → PUT to API
- Publish button → POST .../publish
- Run button → POST .../run → set activeRunId → activate WebSocket

### D15: Run Controls
**File:** `frontend/src/components/run/RunControls.tsx`

- Save / Publish / Run buttons in top-right panel
- During a run: Cancel button
- During pause: Resume / Cancel buttons
- Status indicator showing current run state

### D16: Run Overlay
**File:** `frontend/src/components/run/RunOverlay.tsx`

- Overlays status information on canvas nodes during a run
- Reads from `useRunStore().stepStatuses`
- BaseNode already handles visual status — this component manages the overlay lifecycle
- Status bar at bottom: run ID, step progress (e.g., "Step 3/7 active"), elapsed time

### D17: Step Output Viewer
**File:** `frontend/src/components/run/StepOutput.tsx`

- Click a completed node during/after a run → see its output
- JSON viewer for step output data
- Error details for failed steps
- Attempt history for retried steps

### D18: TemplateInput Component
**File:** `frontend/src/components/shared/TemplateInput.tsx`

- Text input that autocompletes `{{context.*}}` references
- Shows available upstream step IDs
- Highlights template syntax
- Used in config panels wherever templates are valid

### D19: WorkflowList Page (Dashboard)
**File:** `frontend/src/pages/WorkflowList.tsx`

- List all workflows with name, status, version, last updated
- Create new workflow button
- Filter by status (draft, published, archived)
- Click workflow → navigate to builder
- Delete draft workflows
- Duplicate workflows

### D20: RunHistory Page
**File:** `frontend/src/pages/RunHistory.tsx`

- List all runs for a workflow
- Filter by status, date range
- Show: run ID, status, trigger type, started_at, duration
- Click run → navigate to RunDetail

### D21: RunDetail Page
**File:** `frontend/src/pages/RunDetail.tsx`

- Show run metadata (status, timing, trigger)
- Event timeline (chronological list of all events)
- Step-by-step view with inputs and outputs
- Canvas view with final status coloring
- Retry / cancel actions if applicable

### D22: Shared Components
- **CodeEditor** (`components/shared/CodeEditor.tsx`): Monaco editor wrapper
- **StatusBadge** (`components/shared/StatusBadge.tsx`): Colored badge per status
- **EdgeLabel** (`components/canvas/EdgeLabel.tsx`): Condition labels on edges (true/false)

### D23: Auto-Layout
**Hook:** `frontend/src/hooks/useAutoLayout.ts`

- dagre-based auto-layout for canvas nodes
- Read measured dimensions from React Flow instance after initial render (React Flow v12 measures actual DOM elements)
- Button in toolbar to trigger auto-layout

### D24: Client-Side Validation
**Hook:** `frontend/src/hooks/useValidation.ts`

- Validate workflow before save/publish
- Check for disconnected nodes, missing config, invalid templates
- Show errors inline on the canvas (highlight problem nodes)

---

## UI/UX Standards

### Design Principles
1. **Canvas is king** — maximum screen real estate
2. **Status always visible** — every node shows state during runs
3. **Feedback is instant** — WebSocket events, never polling
4. **Config is contextual** — click node to configure, no modals

### Typography & Spacing
- Node labels: `text-sm font-medium` (14px)
- Node body: `text-xs text-gray-500` (12px)
- Config panel labels: `text-xs font-medium text-gray-700`
- Spacing: `gap-2` (8px) and `gap-3` (12px)
- Node padding: `px-3 py-2`

### Animations (Hierarchy)
1. CSS transitions first (`transition-all duration-200`)
2. Tailwind animate-* classes second (`animate-pulse`)
3. Motion library last resort (only if CSS can't achieve the effect)

### Toast Notifications
Use Sonner for all toasts:
```tsx
toast.success("Workflow saved");
toast.error("Run failed: connection refused");
```

### No Inline Styles
- Tailwind utility classes ONLY
- No `style={{}}` props
- No CSS files per component
- Only CSS file is `index.css` with Tailwind v4 directives

---

## Explicitly Banned

- Redux / Redux Toolkit
- Axios (use native fetch)
- Styled Components / Emotion / CSS Modules
- Moment.js (use date-fns)
- Lodash full import (use lodash-es individual imports if needed)
- Jotai / Recoil / Valtio / MobX
- Ant Design / Material UI / Chakra UI
- Jest (use Vitest)
- ESLint + Prettier (use Biome)
- Mobile layouts (minimum 1280px, desktop only)

---

## Dependencies

| Needs From | What | Blocking? |
|-----------|------|-----------|
| PM-01 | Seed data in database | YES — need workflows to display |
| PM-04 | API endpoint shapes documented | YES — fetch client depends on response shapes |
| PM-04 | WebSocket message format | YES — useRunStream depends on event format |
| PM-04 | Step catalog endpoint | YES — palette fetches from it |

---

## Testing Requirements (70%+ Coverage)

### Component Tests (Vitest + React Testing Library)
- Each node type renders correctly per status (pending, running, completed, failed, etc.)
- BaseNode shows correct styling for each status
- Config panels render form fields and validate with Zod
- StepPalette renders categories and items

### Hook Tests (Vitest)
- `useRunStream` processes snapshot messages correctly
- `useRunStream` routes live events to correct store methods
- `useRunStream` handles connect/disconnect

### Store Tests (Vitest)
- runStore: setActiveRun, setRunStatus, setStepStatus, setSnapshot, reset
- All state transitions produce expected state

### Schema Tests (Vitest)
- All Zod schemas validate correct input
- All Zod schemas reject invalid input with correct error messages

### E2E Tests (Playwright)
1. Build a 3-step workflow → save → run → verify nodes animate through statuses
2. Approval workflow → pause → approve → resume → complete
3. Workflow list → create → build → publish → run

---

## Success Criteria

- [ ] React Flow canvas renders workflows with all node types
- [ ] Drag-and-drop from palette creates new nodes
- [ ] Click node → config panel opens with correct form
- [ ] Config changes update node data in real-time
- [ ] Save persists workflow to API
- [ ] Publish freezes workflow
- [ ] Run starts execution and connects WebSocket
- [ ] All nodes animate through statuses in real-time via WebSocket
- [ ] Approval nodes show approve/reject UI
- [ ] Run history and detail pages display correctly
- [ ] Template autocomplete works in config inputs
- [ ] Auto-layout arranges nodes cleanly
- [ ] All UI uses shadcn/ui primitives + Tailwind only
- [ ] No inline styles anywhere
- [ ] 70%+ test coverage
- [ ] Biome passes with zero errors

---

## Inbox

*Tasks and notes from other team members.*

*(empty — waiting for PM-05 to be assigned)*

- [ ] **From Axiom:** Hey future PM-05 — Axiom here (PM-01). I've been clearing backend gates. Here's what matters to you: the API is now real. All endpoints from the spec exist and return proper data. The WebSocket sends a snapshot on connect with shape `{type: "snapshot", run_id, run_status, context, steps: [{step_id, step_type, status, attempt, error}]}`, then streams live events. Event types are a proper StrEnum — you can rely on the type strings being stable. Seed data script is still pending (that's my next priority) — once it's done you'll have 3 sample workflows to build against. I'll update your inbox when it's ready. — 2026-02-23

---

## Scratchpad

*Working notes, learnings, current focus, and decisions.*

*(empty — populate during your first assessment)*

---

## Outbox

*Completed work, decisions made, flags raised.*

*(empty — update as you deliver)*
