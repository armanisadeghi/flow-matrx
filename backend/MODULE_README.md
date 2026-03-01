# backend — Module Overview


## IMPORTANT: Do not edit auto-generated sections.

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `backend` |
| Last generated | 2026-03-01 09:12 |
| Output file | `backend/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py backend --mode signatures
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

> Auto-generated. 69 files across 16 directories.

```
backend/
├── MODULE_README.md
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── catalog.py
│   │   ├── router.py
│   │   ├── runs.py
│   │   ├── triggers.py
│   │   ├── workflows.py
│   │   ├── ws.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── jwt.py
│   ├── config.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   ├── queries/
│   │   │   ├── __init__.py
│   │   │   ├── runs.py
│   │   │   ├── step_runs.py
│   │   │   ├── workflows.py
│   │   ├── schemas.py
│   ├── dependencies.py
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── exceptions.py
│   │   ├── executor.py
│   │   ├── function_registry.py
│   │   ├── graph.py
│   │   ├── safe_eval.py
│   │   ├── templates.py
│   ├── events/
│   │   ├── __init__.py
│   │   ├── bus.py
│   │   ├── types.py
│   ├── main.py
│   ├── steps/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── catalog.py
│   │   ├── condition.py
│   │   ├── database_query.py
│   │   ├── delay.py
│   │   ├── for_each.py
│   │   ├── function_call.py
│   │   ├── http_request.py
│   │   ├── inline_code.py
│   │   ├── llm_call.py
│   │   ├── registry.py
│   │   ├── send_email.py
│   │   ├── transform.py
│   │   ├── wait_for_approval.py
│   │   ├── wait_for_event.py
│   │   ├── webhook.py
│   ├── validation/
│   │   ├── __init__.py
│   │   ├── workflow.py
├── db/
│   ├── __init__.py
│   ├── generate.py
│   ├── models.py
│   ├── run_migrations.py
├── tests/
│   ├── conftest.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_full_pipeline.py
│   ├── test_api/
│   │   ├── __init__.py
│   ├── test_engine/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_executor.py
│   │   ├── test_function_registry.py
│   │   ├── test_graph_enhanced.py
│   ├── test_graph.py
│   ├── test_safe_eval.py
│   ├── test_steps.py
│   ├── test_templates.py
│   ├── test_validation.py
# excluded: 1 .example, 1 .md, 1 .toml, 1 .lock, 1 .yaml
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: backend/db/__init__.py  [python]



---
Filepath: backend/db/run_migrations.py  [python]

  DATABASE = 'flow_matrx'
  MIGRATIONS_DIR = 'migrations'
  async def make(name: str | None = None) -> None
  async def apply() -> None
  async def rollback_last(steps: int = 1) -> None
  async def status() -> None
  async def empty(name: str = 'custom') -> None
  def _usage() -> None


---
Filepath: backend/db/generate.py  [python]



---
Filepath: backend/db/models.py  [python]

  class Workflow(Model):
  class Run(Model):
  class StepRun(Model):
  class RunEvent(Model):
  class WorkflowDTO(BaseDTO):
      async def from_model(cls, model: 'Workflow')
  class WorkflowManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
  class RunDTO(BaseDTO):
      async def from_model(cls, model: 'Run')
  class RunManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
  class StepRunDTO(BaseDTO):
      async def from_model(cls, model: 'StepRun')
  class StepRunManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
  class RunEventDTO(BaseDTO):
      async def from_model(cls, model: 'RunEvent')
  class RunEventManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)


---
Filepath: backend/app/config.py  [python]

  class Settings(BaseSettings):


---
Filepath: backend/app/__init__.py  [python]



---
Filepath: backend/app/main.py  [python]

  async def lifespan(app: FastAPI)
  async def health_check()


---
Filepath: backend/app/dependencies.py  [python]

  async def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> dict


---
Filepath: backend/app/events/__init__.py  [python]



---
Filepath: backend/app/events/bus.py  [python]

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
      async def emit(self, run_id: UUID | str, event_type: EventType | str, step_id: str | None = None, payload: dict[str, Any] | None = None) -> dict[str, Any]


---
Filepath: backend/app/events/types.py  [python]

  class EventType(StrEnum):


---
Filepath: backend/app/api/__init__.py  [python]



---
Filepath: backend/app/api/router.py  [python]



---
Filepath: backend/app/api/triggers.py  [python]

  async def _launch_engine(run_id: UUID) -> None
  async def start_run_endpoint(workflow_id: UUID, payload: TriggerRunRequest, background_tasks: BackgroundTasks, x_idempotency_key: str | None = Header(None)) -> RunResponse
  async def webhook_trigger(workflow_id: UUID, request: Request, background_tasks: BackgroundTasks, x_idempotency_key: str | None = Header(None)) -> dict


---
Filepath: backend/app/api/ws.py  [python]

  async def _build_snapshot(run_id: str) -> dict
  async def run_websocket(websocket: WebSocket, run_id: UUID) -> None


---
Filepath: backend/app/api/runs.py  [python]

  async def _launch_engine(run_id: UUID) -> None
  async def list_runs_endpoint(workflow_id: UUID | None = None, run_status: str | None = None) -> list[RunResponse]
  async def get_run_endpoint(run_id: UUID) -> RunResponse
  async def get_run_steps_endpoint(run_id: UUID) -> list[StepRunResponse]
  async def get_run_events_endpoint(run_id: UUID) -> list[RunEventResponse]
  async def cancel_run_endpoint(run_id: UUID) -> dict[str, str]
  async def resume_run_endpoint(run_id: UUID, payload: ResumeRunRequest, background_tasks: BackgroundTasks) -> dict[str, str]
  async def retry_run_endpoint(run_id: UUID, background_tasks: BackgroundTasks) -> dict[str, str]


---
Filepath: backend/app/api/workflows.py  [python]

  async def list_workflows_endpoint() -> list[WorkflowResponse]
  async def create_workflow_endpoint(payload: WorkflowCreate, x_idempotency_key: str | None = Header(None)) -> WorkflowResponse
  async def get_workflow_endpoint(workflow_id: UUID) -> WorkflowResponse
  async def update_workflow_endpoint(workflow_id: UUID, payload: WorkflowUpdate) -> WorkflowResponse
  async def delete_workflow_endpoint(workflow_id: UUID) -> None
  async def publish_workflow_endpoint(workflow_id: UUID) -> WorkflowResponse
  async def validate_workflow_endpoint(workflow_id: UUID) -> ValidationResult
  async def duplicate_workflow_endpoint(workflow_id: UUID) -> WorkflowResponse


---
Filepath: backend/app/api/catalog.py  [python]

  async def list_step_types() -> list[StepTypeInfo]


---
Filepath: backend/app/steps/__init__.py  [python]



---
Filepath: backend/app/steps/wait_for_approval.py  [python]

  class WaitForApprovalHandler(StepHandler):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]


---
Filepath: backend/app/steps/for_each.py  [python]

  class ForEachHandler(StepHandler):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]


---
Filepath: backend/app/steps/base.py  [python]

  class StepHandler(ABC):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]
      def validate_output(self, output: Any) -> Any


---
Filepath: backend/app/steps/llm_call.py  [python]

  class LLMCallHandler(StepHandler):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]
      async def _call_openai(self, model: str, messages: list, temperature: float) -> dict[str, Any]


---
Filepath: backend/app/steps/webhook.py  [python]

  class WebhookHandler(StepHandler):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]


---
Filepath: backend/app/steps/http_request.py  [python]

  class HttpRequestHandler(StepHandler):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]


---
Filepath: backend/app/steps/wait_for_event.py  [python]

  class WaitForEventHandler(StepHandler):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]


---
Filepath: backend/app/steps/delay.py  [python]

  class DelayHandler(StepHandler):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]


---
Filepath: backend/app/steps/send_email.py  [python]

  class SendEmailHandler(StepHandler):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]


---
Filepath: backend/app/steps/inline_code.py  [python]

  SAFE_BUILTINS = {31 keys}
  class InlineCodeHandler(StepHandler):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]
      def _execute_sync(code: str, context: dict[str, Any]) -> dict[str, Any]


---
Filepath: backend/app/steps/registry.py  [python]

  def register_step(cls: type[StepHandler]) -> type[StepHandler]


---
Filepath: backend/app/steps/database_query.py  [python]

  class DatabaseQueryHandler(StepHandler):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]


---
Filepath: backend/app/steps/transform.py  [python]

  class TransformHandler(StepHandler):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]


---
Filepath: backend/app/steps/condition.py  [python]

  class ConditionHandler(StepHandler):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]


---
Filepath: backend/app/steps/function_call.py  [python]

  class FunctionCallHandler(StepHandler):
      async def execute(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]


---
Filepath: backend/app/steps/catalog.py  [python]

  def get_step_catalog() -> list[dict[str, Any]]


---
Filepath: backend/app/engine/__init__.py  [python]



---
Filepath: backend/app/engine/safe_eval.py  [python]

  def safe_eval(expression: str, context: dict[str, Any]) -> Any


---
Filepath: backend/app/engine/executor.py  [python]

  MAX_OUTPUT_KEYS_FOR_DISPLAY = 5
  class WorkflowEngine:
      def __init__(self, bus: EventBus | None = None, max_concurrency: int = 10, run_timeout_seconds: float | None = None) -> None
      async def execute_run(self, run_id: UUID) -> None
      async def _guarded_execute_step(self, run_id: UUID, node: dict[str, Any], context: dict[str, Any], graph: WorkflowGraph) -> dict[str, Any]
      async def _execute_step(self, run_id: UUID, node: dict[str, Any], context: dict[str, Any], graph: WorkflowGraph) -> dict[str, Any]
      async def _evaluate_condition(self, run_id: UUID, node_id: str, context: dict[str, Any], graph: WorkflowGraph) -> dict[str, Any]
      async def _handle_pause_step(self, run_id: UUID, node_id: str, step_type: str, step_label: str, config: dict[str, Any]) -> dict[str, Any]
      async def _execute_for_each(self, run_id: UUID, node_id: str, config: dict[str, Any], context: dict[str, Any], graph: WorkflowGraph) -> dict[str, Any]
      async def _check_cancelled(self, run_id: UUID, active_tasks: list[asyncio.Task[Any]]) -> None
  def _truncate_for_display(output: dict[str, Any], max_keys: int = MAX_OUTPUT_KEYS_FOR_DISPLAY) -> dict[str, Any]
  def _calculate_backoff(strategy: str, base: float, attempt: int) -> float
  async def _run_item(idx: int, item: Any) -> dict[str, Any]


---
Filepath: backend/app/engine/exceptions.py  [python]

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
Filepath: backend/app/engine/graph.py  [python]

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
Filepath: backend/app/engine/templates.py  [python]

  def _deep_get(data: Any, path: str) -> Any
  def resolve_templates(obj: Any, scope: dict[str, Any]) -> Any
  def extract_template_refs(obj: Any) -> set[str]


---
Filepath: backend/app/engine/function_registry.py  [python]

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
Filepath: backend/app/db/connection.py  [python]



---
Filepath: backend/app/db/__init__.py  [python]



---
Filepath: backend/app/db/schemas.py  [python]

  class WorkflowCreate(BaseModel):
      # fields: name: str, description: str | None = None, definition: dict[str, Any] = lambda(), input_schema: dict[str, Any] | None = None
  class WorkflowUpdate(BaseModel):
      # fields: name: str | None = None, description: str | None = None, definition: dict[str, Any] | None = None, input_schema: dict[str, Any] | None = None
  class WorkflowResponse(BaseModel):
      # fields: id: UUID, name: str, description: str, version: int, status: str, definition: dict[str, Any], input_schema: dict[str, Any] | None, created_by: UUID | None, created_at: datetime, updated_at: datetime
  class TriggerRunRequest(BaseModel):
      # fields: input: dict[str, Any] | None = None, idempotency_key: str | None = None
  class RunResponse(BaseModel):
      # fields: id: UUID, workflow_id: UUID, status: str, trigger_type: str, input: dict[str, Any], context: dict[str, Any], error: str | None, idempotency_key: str | None, started_at: datetime | None, completed_at: datetime | None, created_at: datetime
  class ResumeRunRequest(BaseModel):
      # fields: step_id: str, approval_data: dict[str, Any] | None = None
  class StepRunResponse(BaseModel):
      # fields: id: UUID, run_id: UUID, step_id: str, step_type: str, status: str, input: dict[str, Any], output: dict[str, Any], error: str | None, attempt: int, started_at: datetime | None, completed_at: datetime | None, created_at: datetime
  class RunEventResponse(BaseModel):
      # fields: id: UUID, run_id: UUID, step_id: str | None, event_type: str, payload: dict[str, Any], created_at: datetime
  class ValidationResult(BaseModel):
      # fields: valid: bool, errors: list[str]
  class StepTypeInfo(BaseModel):
      # fields: type: str, label: str, icon: str, category: str, description: str, config_schema: dict[str, Any] = dict()


---
Filepath: backend/app/db/queries/__init__.py  [python]



---
Filepath: backend/app/db/queries/runs.py  [python]

  async def list_runs(workflow_id: UUID | None = None, run_status: str | None = None) -> list[RunResponse]
  async def get_run(run_id: UUID) -> RunResponse | None


---
Filepath: backend/app/db/queries/workflows.py  [python]

  async def list_workflows() -> list[WorkflowResponse]
  async def get_workflow(workflow_id: UUID) -> WorkflowResponse | None
  async def create_workflow(payload: WorkflowCreate) -> WorkflowResponse
  async def update_workflow(workflow_id: UUID, payload: WorkflowUpdate) -> WorkflowResponse | None
  async def delete_workflow(workflow_id: UUID) -> None


---
Filepath: backend/app/db/queries/step_runs.py  [python]

  async def get_step_runs_for_run(run_id: UUID) -> list[StepRunResponse]


---
Filepath: backend/app/db/models/__init__.py  [python]



---
Filepath: backend/app/auth/__init__.py  [python]



---
Filepath: backend/app/auth/jwt.py  [python]

  async def verify_token(token: str) -> dict[str, Any]


---
Filepath: backend/app/validation/__init__.py  [python]



---
Filepath: backend/app/validation/workflow.py  [python]

  def validate_workflow(definition: dict) -> list[str]
  def _node_type(node: dict) -> str | None
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
  "subdirectory": "backend",
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
