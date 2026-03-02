# app — Module Overview


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
| Last generated | 2026-03-01 15:50 |
| Output file | `MODULE_README.md` |
| Signature mode | `signatures` |


**Child READMEs detected** (signatures collapsed — see links for detail):

| README | |
|--------|---|
| [`db/MODULE_README.md`](db/MODULE_README.md) | last generated 2026-03-01 15:50 |
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

> Auto-generated. 65 files across 12 directories.

```
./
├── MODULE_README.md
├── __init__.py
├── api/
│   ├── __init__.py
│   ├── catalog.py
│   ├── router.py
│   ├── runs.py
│   ├── triggers.py
│   ├── workflows.py
│   ├── ws.py
├── auth/
│   ├── __init__.py
│   ├── jwt.py
├── bootstrap.py
├── config.py
├── db/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── custom/
│   │   ├── __init__.py
│   │   ├── core.py
│   │   ├── user.py
│   ├── fields.py
│   ├── generate.py
│   ├── helpers/
│   │   ├── auto_config.py
│   ├── jsonb_types.py
│   ├── managers/
│   │   ├── __init__.py
│   │   ├── org.py
│   │   ├── org_member.py
│   │   ├── resource_share.py
│   │   ├── user_profile.py
│   │   ├── wf_run.py
│   │   ├── wf_run_event.py
│   │   ├── wf_step_run.py
│   │   ├── wf_workflow.py
│   ├── models.py
│   ├── run_migrations.py
├── dependencies.py
├── engine/
│   ├── __init__.py
│   ├── exceptions.py
│   ├── executor.py
│   ├── function_registry.py
│   ├── graph.py
│   ├── safe_eval.py
│   ├── templates.py
├── events/
│   ├── __init__.py
│   ├── bus.py
│   ├── types.py
├── main.py
├── steps/
│   ├── __init__.py
│   ├── base.py
│   ├── catalog.py
│   ├── condition.py
│   ├── database_query.py
│   ├── delay.py
│   ├── for_each.py
│   ├── function_call.py
│   ├── http_request.py
│   ├── inline_code.py
│   ├── llm_call.py
│   ├── registry.py
│   ├── send_email.py
│   ├── transform.py
│   ├── wait_for_approval.py
│   ├── wait_for_event.py
│   ├── webhook.py
├── types/
│   ├── schemas.py
├── validation/
│   ├── __init__.py
│   ├── workflow.py
# excluded: 2 .md, 1 .yaml
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="{mode}"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.
> Submodules with their own `MODULE_README.md` are collapsed to a single stub line.

```
---
Filepath: config.py  [python]

  class DatabaseSettings(BaseSettings):
      def url(self) -> str
  class SupabaseSettings(BaseSettings):
      def configured(self) -> bool
  class RedisSettings(BaseSettings):
  class LLMSettings(BaseSettings):
      def key_for(self, provider: str) -> str
  class LogSettings(BaseSettings):
      def validate_level(cls, v: str) -> str
      def validate_format(cls, v: str) -> str
  class DirectorySettings:
      def __init__(self, base_dir: Path) -> None
      def create_all(self) -> None
      def __repr__(self) -> str
  class Settings(BaseSettings):
      def validate_app_env(cls, v: str) -> str
      def _build_dirs(self) -> Settings
  def get_settings() -> Settings



---
Filepath: __init__.py  [python]




---
Filepath: bootstrap.py  [python]

  class _MatrxSettingsAdapter:
      def __init__(self, app_settings: object) -> None
      def __getattr__(self, name: str) -> object
  def bootstrap() -> None



---
Filepath: main.py  [python]

  async def lifespan(app: FastAPI)
  async def health_check()



---
Filepath: dependencies.py  [python]

  async def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> dict



---
Filepath: events/__init__.py  [python]




---
Filepath: events/bus.py  [python]

  class EventPersister(Protocol):
      async def insert_run_event(self, run_id: str, event_type: str, step_id: str | None, payload: dict[str, Any]) -> None
  class _DefaultPersister:
      async def insert_run_event(self, run_id: str, event_type: str, step_id: str | None, payload: dict[str, Any]) -> None
  class EventBus:
      def __init__(self, persister: EventPersister | None = None) -> None
      def subscribe(self, run_id: str, queue: asyncio.Queue[dict[str, Any]] | None = None) -> asyncio.Queue[dict[str, Any]]
      def unsubscribe(self, run_id: str, queue: asyncio.Queue[dict[str, Any]]) -> None
      def add_listener(self, callback: Callable[[dict[str, Any]], Coroutine[Any, Any, None]]) -> None
      def remove_listener(self, callback: Callable[[dict[str, Any]], Coroutine[Any, Any, None]]) -> None
      async def emit(self, run_id: str | str, event_type: EventType | str, step_id: str | None = None, payload: dict[str, Any] | None = None) -> dict[str, Any]



---
Filepath: events/types.py  [python]

  class EventType(StrEnum):



---
Filepath: api/__init__.py  [python]




---
Filepath: api/router.py  [python]




---
Filepath: api/triggers.py  [python]

  async def _launch_engine(run_id: str) -> None
  async def start_run_endpoint(workflow_id: str, payload: TriggerRunRequest, background_tasks: BackgroundTasks, x_idempotency_key: str | None = Header(None)) -> RunResponse
  async def webhook_trigger(workflow_id: str, request: Request, background_tasks: BackgroundTasks, x_idempotency_key: str | None = Header(None)) -> dict



---
Filepath: api/ws.py  [python]

  async def _build_snapshot(run_id: str) -> dict
  async def run_websocket(websocket: WebSocket, run_id: str) -> None



---
Filepath: api/runs.py  [python]

  async def _launch_engine(run_id: str) -> None
  async def list_runs_endpoint(workflow_id: str | None = None, run_status: str | None = None) -> list[RunResponse]
  async def get_run_endpoint(run_id: str) -> RunResponse
  async def get_run_steps_endpoint(run_id: str) -> list[StepRunResponse]
  async def get_run_events_endpoint(run_id: str) -> list[RunEventResponse]
  async def cancel_run_endpoint(run_id: str) -> dict[str, str]
  async def resume_run_endpoint(run_id: str, payload: ResumeRunRequest, background_tasks: BackgroundTasks) -> dict[str, str]
  async def retry_run_endpoint(run_id: str, background_tasks: BackgroundTasks) -> dict[str, str]



---
Filepath: api/workflows.py  [python]

  async def list_workflows_endpoint() -> list[WorkflowResponse]
  async def create_workflow_endpoint(payload: WorkflowCreate, x_idempotency_key: str | None = Header(None)) -> WorkflowResponse
  async def get_workflow_endpoint(workflow_id: str) -> WorkflowResponse
  async def update_workflow_endpoint(workflow_id: str, payload: WorkflowUpdate) -> WorkflowResponse
  async def delete_workflow_endpoint(workflow_id: str) -> None
  async def publish_workflow_endpoint(workflow_id: str) -> WorkflowResponse
  async def validate_workflow_endpoint(workflow_id: str) -> ValidationResult
  async def duplicate_workflow_endpoint(workflow_id: str) -> WorkflowResponse



---
Filepath: api/catalog.py  [python]

  async def list_step_types() -> list[StepTypeInfo]



---
Filepath: types/schemas.py  [python]

  class WorkflowCreate(BaseModel):
      # fields: name: str, description: str | None = None, definition: dict[str, Any] = lambda(), input_schema: dict[str, Any] | None = None
  class WorkflowUpdate(BaseModel):
      # fields: name: str | None = None, description: str | None = None, definition: dict[str, Any] | None = None, input_schema: dict[str, Any] | None = None
  class WorkflowResponse(BaseModel):
      # fields: id: str, name: str, description: str, version: int, status: str, definition: dict[str, Any], input_schema: dict[str, Any] | None, created_by: str | None, created_at: datetime, updated_at: datetime
  class TriggerRunRequest(BaseModel):
      # fields: input: dict[str, Any] | None = None, idempotency_key: str | None = None
  class RunResponse(BaseModel):
      # fields: id: str, workflow_id: str, status: str, trigger_type: str, input: dict[str, Any], context: dict[str, Any], error: str | None, idempotency_key: str | None, created_by: str | None, started_at: datetime | None, completed_at: datetime | None, created_at: datetime
  class ResumeRunRequest(BaseModel):
      # fields: step_id: str, approval_data: dict[str, Any] | None = None
  class StepRunResponse(BaseModel):
      # fields: id: str, run_id: str, step_id: str, step_type: str, status: str, input: dict[str, Any], output: dict[str, Any], error: str | None, attempt: int, started_at: datetime | None, completed_at: datetime | None, created_at: datetime
  class RunEventResponse(BaseModel):
      # fields: id: str, run_id: str, step_id: str | None, event_type: str, payload: dict[str, Any], created_at: datetime
  class ValidationResult(BaseModel):
      # fields: valid: bool, errors: list[str]
  class StepTypeInfo(BaseModel):
      # fields: type: str, label: str, icon: str, category: str, description: str, config_schema: dict[str, Any] = dict()



---
Filepath: steps/__init__.py  [python]




---
Filepath: steps/wait_for_approval.py  [python]

  class WaitForApprovalHandler(StepHandler):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]



---
Filepath: steps/for_each.py  [python]

  class ForEachHandler(StepHandler):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]



---
Filepath: steps/base.py  [python]

  class StepHandler(ABC):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]
      def validate_output(self, output: Any) -> Any



---
Filepath: steps/llm_call.py  [python]

  class LLMCallHandler(StepHandler):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]
      async def _call_openai(self, model: str, messages: list, temperature: float) -> dict[str, Any]



---
Filepath: steps/webhook.py  [python]

  class WebhookHandler(StepHandler):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]



---
Filepath: steps/http_request.py  [python]

  class HttpRequestHandler(StepHandler):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]



---
Filepath: steps/wait_for_event.py  [python]

  class WaitForEventHandler(StepHandler):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]



---
Filepath: steps/delay.py  [python]

  class DelayHandler(StepHandler):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]



---
Filepath: steps/send_email.py  [python]

  class SendEmailHandler(StepHandler):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]



---
Filepath: steps/inline_code.py  [python]

  SAFE_BUILTINS = {31 keys}
  class InlineCodeHandler(StepHandler):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]
      def _execute_sync(code: str, context: dict[str, Any]) -> dict[str, Any]



---
Filepath: steps/registry.py  [python]

  def register_step(cls: type[StepHandler]) -> type[StepHandler]



---
Filepath: steps/database_query.py  [python]

  class DatabaseQueryHandler(StepHandler):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]



---
Filepath: steps/transform.py  [python]

  class TransformHandler(StepHandler):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]



---
Filepath: steps/condition.py  [python]

  class ConditionHandler(StepHandler):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]



---
Filepath: steps/function_call.py  [python]

  class FunctionCallHandler(StepHandler):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]



---
Filepath: steps/catalog.py  [python]

  def get_step_catalog() -> list[dict[str, Any]]



---
Filepath: engine/__init__.py  [python]




---
Filepath: engine/safe_eval.py  [python]

  def safe_eval(expression: str, context: dict[str, Any]) -> Any



---
Filepath: engine/executor.py  [python]

  MAX_OUTPUT_KEYS_FOR_DISPLAY = 5
  class WorkflowEngine:
      def __init__(self, bus: EventBus | None = None, max_concurrency: int = 10, run_timeout_seconds: float | None = None) -> None
      async def execute_run(self, run_id: str) -> None
      async def _guarded_execute_step(self, run_id: str, node: dict[str, Any], context: dict[str, Any], graph: WorkflowGraph) -> dict[str, Any]
      async def _execute_step(self, run_id: str, node: dict[str, Any], context: dict[str, Any], graph: WorkflowGraph) -> dict[str, Any]
      async def _evaluate_condition(self, run_id: str, node_id: str, context: dict[str, Any], graph: WorkflowGraph) -> dict[str, Any]
      async def _handle_pause_step(self, run_id: str, node_id: str, step_type: str, step_label: str, config: dict[str, Any]) -> dict[str, Any]
      async def _execute_for_each(self, run_id: str, node_id: str, config: dict[str, Any], context: dict[str, Any], graph: WorkflowGraph) -> dict[str, Any]
      async def _check_cancelled(self, run_id: str, active_tasks: list[asyncio.Task[Any]]) -> None
  def _truncate_for_display(output: dict[str, Any], max_keys: int = MAX_OUTPUT_KEYS_FOR_DISPLAY) -> dict[str, Any]
  def _calculate_backoff(strategy: str, base: float, attempt: int) -> float
  async def _run_item(idx: int, item: Any) -> dict[str, Any]



---
Filepath: engine/exceptions.py  [python]

  class EngineError(Exception):
  class PauseExecution(EngineError):
      def __init__(self, step_id: str, reason: str = '', pause_type: str = 'approval') -> None
  class StepTimeout(EngineError):
      def __init__(self, step_id: str, timeout_seconds: float) -> None
  class WorkflowValidationError(EngineError):
      def __init__(self, errors: list[str]) -> None
  class RetriableError(EngineError):
      def __init__(self, message: str, original: Exception | None = None) -> None
  class NonRetriableError(EngineError):
      def __init__(self, message: str, original: Exception | None = None) -> None
  class RunCancelled(EngineError):
  class RunTimeout(EngineError):
      def __init__(self, run_id: str, timeout_seconds: float) -> None



---
Filepath: engine/graph.py  [python]

  class WorkflowGraph:
      def __init__(self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> None
      def get_node(self, node_id: str) -> dict[str, Any]
      def get_node_type(self, node_id: str) -> str
      def get_node_data(self, node_id: str) -> dict[str, Any]
      def get_node_config(self, node_id: str) -> dict[str, Any]
      def get_node_label(self, node_id: str) -> str
      def node_ids(self) -> set[str]
      def node_count(self) -> int
      def edge_count(self) -> int
      def get_ready_steps(self, done_ids: set[str]) -> list[dict[str, Any]]
      def get_downstream(self, node_id: str) -> list[str]
      def get_upstream(self, node_id: str) -> list[str]
      def get_outgoing_edges(self, node_id: str) -> list[dict[str, Any]]
      def get_incoming_edges(self, node_id: str) -> list[dict[str, Any]]
      def topological_sort(self) -> list[str]
      def has_cycle(self) -> bool
      def execution_levels(self) -> list[list[str]]
      def get_branch_nodes(self, condition_id: str, branch_label: str) -> set[str]
      def get_exclusive_branch_nodes(self, condition_id: str, branch_label: str) -> set[str]
      def _all_descendants(self, node_id: str) -> set[str]
      def get_upstream_ids(self, node_id: str) -> set[str]
      def subgraph(self, node_ids: set[str]) -> WorkflowGraph
      def get_nodes_by_type(self, step_type: str) -> list[dict[str, Any]]
      def get_critical_path(self) -> list[str]



---
Filepath: engine/templates.py  [python]

  def _deep_get(data: Any, path: str) -> Any
  def resolve_templates(obj: Any, scope: dict[str, Any]) -> Any
  def extract_template_refs(obj: Any) -> set[str]



---
Filepath: engine/function_registry.py  [python]

  FunctionType = Callable[[dict[str, Any], dict[str, Any]], Coroutine[Any, Any, dict[str, Any]]]
  class FunctionNotFoundError(Exception):
  class FunctionValidationError(Exception):
  class FunctionRegistry:
      def __init__(self) -> None
      def registered_names(self) -> list[str]
      def register(self, import_path: str, name: str | None = None, metadata: dict[str, Any] | None = None) -> None
      def register_callable(self, name: str, func: FunctionType, metadata: dict[str, Any] | None = None) -> None
      def register_many(self, entries: list[dict[str, Any]]) -> None
      def get(self, name: str) -> FunctionType
      def has(self, name: str) -> bool
      def get_metadata(self, name: str) -> dict[str, Any]
      def get_catalog(self) -> list[dict[str, Any]]
      def unregister(self, name: str) -> None
      def clear(self) -> None
      def _import_callable(import_path: str) -> FunctionType
  def register_function(name: str | None = None, metadata: dict[str, Any] | None = None) -> Callable[[FunctionType], FunctionType]
  def decorator(func: FunctionType) -> FunctionType



---
Submodule: db/  [19 files — full detail in db/MODULE_README.md]

---
Filepath: auth/__init__.py  [python]




---
Filepath: auth/jwt.py  [python]

  async def verify_token(token: str) -> dict[str, Any]



---
Filepath: validation/__init__.py  [python]




---
Filepath: validation/workflow.py  [python]

  def validate_workflow(definition: dict) -> ValidationResult
  def _node_type(node: dict) -> str | None
```
<!-- /AUTO:signatures -->

<!-- AUTO:callers -->
## Upstream Callers

> Auto-discovered by scanning all project files that import from this module.
> Set `ENTRY_POINTS` in `generate_readme.py` to pin specific functions.

| Caller | Calls |
|--------|-------|
| `tests/integration/test_full_pipeline.py` | `EventBus()` |
| `tests/test_engine/test_executor.py` | `EventBus()` |
| `tests/integration/test_full_pipeline.py` | `EventType()` |
| `tests/test_engine/test_function_registry.py` | `FunctionCallHandler()` |
| `tests/test_engine/test_function_registry.py` | `FunctionNotFoundError()` |
| `tests/test_engine/test_function_registry.py` | `FunctionRegistry()` |
| `tests/test_engine/test_function_registry.py` | `FunctionValidationError()` |
| `tests/test_steps.py` | `HttpRequestHandler()` |
| `tests/test_steps.py` | `InlineCodeHandler()` |
| `tests/test_steps.py` | `LLMCallHandler()` |
| `tests/integration/test_full_pipeline.py` | `PauseExecution()` |
| `tests/test_steps.py` | `StepHandler()` |
| `tests/test_engine/test_executor.py` | `WorkflowEngine()` |
| `tests/integration/test_full_pipeline.py` | `WorkflowGraph()` |
| `tests/test_engine/test_graph_enhanced.py` | `WorkflowGraph()` |
| `tests/test_graph.py` | `WorkflowGraph()` |
| `tests/integration/test_full_pipeline.py` | `extract_template_refs()` |
| `tests/test_templates.py` | `extract_template_refs()` |
| `tests/test_engine/test_function_registry.py` | `register_function()` |
| `tests/integration/test_full_pipeline.py` | `resolve_templates()` |
| `tests/test_templates.py` | `resolve_templates()` |
| `tests/integration/test_full_pipeline.py` | `safe_eval()` |
| `tests/test_safe_eval.py` | `safe_eval()` |
| `tests/integration/test_full_pipeline.py` | `validate_workflow()` |
| `tests/test_validation.py` | `validate_workflow()` |
<!-- /AUTO:callers -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** app, fastapi, httpx, jinja2, matrx_orm, matrx_utils, pydantic, pydantic_settings, structlog
**Internal modules:** db.models
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
    "tests",
    "logs",
    "migrations",
    "reports",
    "sample_data",
    "temp",
    "tmp"
  ],
  "signatures_exclude": [
    "tests",
    "logs",
    "migrations",
    "reports",
    "sample_data",
    "temp",
    "tmp"
  ]
}
```
<!-- /AUTO:config -->
