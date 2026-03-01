#  — Module Overview


## IMPORTANT: Do not edit auto-generated sections.

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `` |
| Last generated | 2026-03-01 09:12 |
| Output file | `MODULE_README.md` |
| Signature mode | `signatures` |


**Child READMEs detected** (signatures collapsed — see links for detail):

| README | |
|--------|---|
| [`backend/MODULE_README.md`](backend/MODULE_README.md) | last generated 2026-03-01 09:12 |
| [`frontend/MODULE_README.md`](frontend/MODULE_README.md) | last generated 2026-03-01 09:12 |
**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py  --mode signatures
```

**To add permanent notes:** Write anywhere outside the `<!-- AUTO:... -->` blocks.
<!-- /AUTO:meta -->

<!-- HUMAN-EDITABLE: This section is yours. Agents & Humans can edit this section freely — it will not be overwritten. -->

## Architecture

> **Fill this in.** Describe the execution flow and layer map for this module.
> See `utils/code_context/MODULE_README_SPEC.md` for the recommended format.
>
> Suggested structure:
>
> ### Layers
> | File | Role |
> |------|------|
> | `entry.py` | Public entry point — receives requests, returns results |
> | `engine.py` | Core dispatch logic |
> | `models.py` | Shared data types |
>
> ### Call Flow (happy path)
> ```
> entry_function() → engine.dispatch() → implementation()
> ```


<!-- AUTO:tree -->
## Directory Tree

> Auto-generated. 127 files across 33 directories.

```
./
├── .arman/
│   ├── open/
│   │   ├── tech-stack/
│   ├── team/
│   │   ├── EXPERTS/
│   │   ├── PMS/
├── .claude/
├── MODULE_README.md
├── backend/
│   ├── MODULE_README.md
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── catalog.py
│   │   │   ├── router.py
│   │   │   ├── runs.py
│   │   │   ├── triggers.py
│   │   │   ├── workflows.py
│   │   │   ├── ws.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── jwt.py
│   │   ├── config.py
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── connection.py
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   ├── queries/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── runs.py
│   │   │   │   ├── step_runs.py
│   │   │   │   ├── workflows.py
│   │   │   ├── schemas.py
│   │   ├── dependencies.py
│   │   ├── engine/
│   │   │   ├── __init__.py
│   │   │   ├── exceptions.py
│   │   │   ├── executor.py
│   │   │   ├── function_registry.py
│   │   │   ├── graph.py
│   │   │   ├── safe_eval.py
│   │   │   ├── templates.py
│   │   ├── events/
│   │   │   ├── __init__.py
│   │   │   ├── bus.py
│   │   │   ├── types.py
│   │   ├── main.py
│   │   ├── steps/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── catalog.py
│   │   │   ├── condition.py
│   │   │   ├── database_query.py
│   │   │   ├── delay.py
│   │   │   ├── for_each.py
│   │   │   ├── function_call.py
│   │   │   ├── http_request.py
│   │   │   ├── inline_code.py
│   │   │   ├── llm_call.py
│   │   │   ├── registry.py
│   │   │   ├── send_email.py
│   │   │   ├── transform.py
│   │   │   ├── wait_for_approval.py
│   │   │   ├── wait_for_event.py
│   │   │   ├── webhook.py
│   │   ├── validation/
│   │   │   ├── __init__.py
│   │   │   ├── workflow.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── generate.py
│   │   ├── models.py
│   │   ├── run_migrations.py
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── integration/
│   │   │   ├── __init__.py
│   │   │   ├── test_full_pipeline.py
│   │   ├── test_api/
│   │   │   ├── __init__.py
│   │   ├── test_engine/
│   │   │   ├── __init__.py
│   │   │   ├── conftest.py
│   │   │   ├── test_executor.py
│   │   │   ├── test_function_registry.py
│   │   │   ├── test_graph_enhanced.py
│   │   ├── test_graph.py
│   │   ├── test_safe_eval.py
│   │   ├── test_steps.py
│   │   ├── test_templates.py
│   │   ├── test_validation.py
├── frontend/
│   ├── MODULE_README.md
│   ├── index.html
│   ├── public/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   ├── runs.ts
│   │   │   ├── workflows.ts
│   │   │   ├── ws.ts
│   │   ├── components/
│   │   │   ├── canvas/
│   │   │   │   ├── Canvas.tsx
│   │   │   │   ├── EdgeLabel.tsx
│   │   │   │   ├── NodeConfigPanel.tsx
│   │   │   │   ├── RunOverlay.tsx
│   │   │   │   ├── StepPalette.tsx
│   │   │   ├── run/
│   │   │   │   ├── ConnectionIndicator.tsx
│   │   │   │   ├── RunControls.tsx
│   │   │   │   ├── StepOutput.tsx
│   │   │   ├── shared/
│   │   │   │   ├── CodeEditor.tsx
│   │   │   │   ├── StatusBadge.tsx
│   │   │   │   ├── TemplateInput.tsx
│   │   ├── config-panels/
│   │   │   ├── ApprovalConfig.tsx
│   │   │   ├── ConditionConfig.tsx
│   │   │   ├── DatabaseQueryConfig.tsx
│   │   │   ├── HttpRequestConfig.tsx
│   │   │   ├── InlineCodeConfig.tsx
│   │   │   ├── LLMCallConfig.tsx
│   │   │   ├── index.ts
│   │   ├── hooks/
│   │   │   ├── useAutoLayout.ts
│   │   │   ├── useRunStream.ts
│   │   │   ├── useValidation.ts
│   │   │   ├── useWorkflow.ts
│   │   ├── lib/
│   │   │   ├── constants.ts
│   │   │   ├── graph-utils.ts
│   │   │   ├── templates.ts
│   │   │   ├── utils.ts
│   │   ├── main.tsx
│   │   ├── nodes/
│   │   │   ├── ApprovalNode.tsx
│   │   │   ├── BaseNode.tsx
│   │   │   ├── ConditionNode.tsx
│   │   │   ├── DatabaseQueryNode.tsx
│   │   │   ├── DelayNode.tsx
│   │   │   ├── HttpRequestNode.tsx
│   │   │   ├── InlineCodeNode.tsx
│   │   │   ├── LLMCallNode.tsx
│   │   │   ├── index.ts
│   │   ├── pages/
│   │   │   ├── RunDetail.tsx
│   │   │   ├── RunHistory.tsx
│   │   │   ├── WorkflowBuilder.tsx
│   │   │   ├── WorkflowList.tsx
│   │   ├── stores/
│   │   │   ├── runStore.ts
│   │   │   ├── workflowStore.ts
│   │   ├── types/
│   │   │   ├── index.ts
│   ├── vite.config.ts
├── packages/
│   ├── shared/
│   │   ├── types/
│   │   │   ├── events.ts
│   │   │   ├── run.ts
│   │   │   ├── workflow.ts
├── scripts/
│   ├── run-migration.sh
│   ├── seed-workflow.py
├── utils_dev/
│   ├── generate_readme.py
# excluded: 41 .md, 7 .json, 3 .yaml, 2 .example, 2 (no ext), 1 .yml, 1 .toml, 1 .lock, 1 .css, 1 .svg
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="{mode}"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.
> Submodules with their own `MODULE_README.md` are collapsed to a single stub line.

```
---
Filepath: utils_dev/generate_readme.py  [python]




---
Filepath: scripts/run-migration.sh  [unknown (.sh)]

  # signature extraction not supported for this language



---
Filepath: scripts/seed-workflow.py  [python]

  SAMPLE_WORKFLOW = {3 keys}
  async def seed()



---
Filepath: packages/shared/types/run.ts  [typescript]

  export type RunStatus = | "pending" | "running" | "paused" | "completed" | "failed" | "cancelled"
  export type StepRunStatus = | "pending" | "running" | "completed" | "failed" | "skipped" | "waiting_approval"
  export interface StepRun
  export interface Run



---
Filepath: packages/shared/types/events.ts  [typescript]

  export type WebSocketEventType = | "snapshot" | "run.started" | "run.completed" | "run.failed" | "run.paused" | "run.resumed" | "run.cancelled" | "step.started" | "step.completed" | "step.failed" | "step.skipped" | "step.waiting" | "step.retrying" | "context.updated"
  export interface SnapshotStep
  export interface SnapshotEvent
  export interface BaseEvent
  export interface RunStatusEvent extends BaseEvent
  export interface StepStatusEvent extends BaseEvent
  export interface ContextUpdatedEvent extends BaseEvent
  export type LiveEvent = RunStatusEvent | StepStatusEvent | ContextUpdatedEvent
  export type WorkflowEvent = SnapshotEvent | LiveEvent



---
Filepath: packages/shared/types/workflow.ts  [typescript]

  export type StepType = | "http_request" | "llm_call" | "inline_code" | "condition" | "database_query" | "transform" | "wait_for_approval" | "wait_for_event" | "send_email" | "webhook" | "delay" | "for_each"
  export interface WorkflowNode
  export interface WorkflowEdge
  export interface WorkflowDefinition



---
Submodule: backend/  [54 files — full detail in backend/MODULE_README.md]

---
Submodule: frontend/  [50 files — full detail in frontend/MODULE_README.md]

```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** 354 packages — see project dependency files for the full list.
**Internal modules:** frontend
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "",
  "mode": "signatures",
  "scope": null,
  "project_noise": null,
  "include_call_graph": false,
  "entry_points": null,
  "call_graph_exclude": [
    "tests"
  ],
  "signatures_exclude": [
    "tests"
  ]
}
```
<!-- /AUTO:config -->
