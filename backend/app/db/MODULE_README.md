# db — Module Overview


## IMPORTANT: Do not edit auto-generated sections.

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `db` |
| Last generated | 2026-03-01 15:50 |
| Output file | `db/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py db --mode signatures
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

> Auto-generated. 19 files across 4 directories.

```
db/
├── __init__.py
├── custom/
│   ├── __init__.py
│   ├── core.py
│   ├── user.py
├── fields.py
├── generate.py
├── helpers/
│   ├── auto_config.py
├── jsonb_types.py
├── managers/
│   ├── __init__.py
│   ├── org.py
│   ├── org_member.py
│   ├── resource_share.py
│   ├── user_profile.py
│   ├── wf_run.py
│   ├── wf_run_event.py
│   ├── wf_step_run.py
│   ├── wf_workflow.py
├── models.py
├── run_migrations.py
# excluded: 1 .yaml
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: db/__init__.py  [python]



---
Filepath: db/fields.py  [python]

  class TypedJSONBField(JSONBField, Generic[T]):
      def __init__(self, dataclass_type: type[T], **kwargs: Any) -> None
      def to_python(self, value: Any) -> T | None
      def get_db_prep_value(self, value: Any) -> Any


---
Filepath: db/run_migrations.py  [python]

  DATABASE = 'flow_matrx'
  MIGRATIONS_DIR = 'migrations'
  MANAGED_TABLES = {'wf_workflows', 'wf_runs', 'wf_step_runs', 'wf_run_events'}
  async def make(name: str | None = None) -> None
  async def apply() -> None
  async def rollback_last(steps: int = 1) -> None
  async def status() -> None
  async def empty(name: str = 'custom') -> None
  def _usage() -> None


---
Filepath: db/jsonb_types.py  [python]

  class OrgMetadata:
  class UserProfileMetadata:
  class WfWorkflowDefinition:
  class WfWorkflowInputSchema:
  class WfRunInput:
  class WfRunContext:
  class WfRunEventPayload:
  class WfStepRunInput:
  class WfStepRunOutput:


---
Filepath: db/generate.py  [python]



---
Filepath: db/models.py  [python]

  class Users(Model):
  class Org(Model):
  class UserProfile(Model):
  class OrgMember(Model):
  class ResourceShare(Model):
  class WfWorkflow(Model):
  class WfRun(Model):
  class WfRunEvent(Model):
  class WfStepRun(Model):
  class OrgDTO(BaseDTO):
      async def from_model(cls, model: Model)
  class OrgManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: Org) -> None
  class UserProfileDTO(BaseDTO):
      async def from_model(cls, model: Model)
  class UserProfileManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: UserProfile) -> None
  class OrgMemberDTO(BaseDTO):
      async def from_model(cls, model: Model)
  class OrgMemberManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: OrgMember) -> None
  class ResourceShareDTO(BaseDTO):
      async def from_model(cls, model: Model)
  class ResourceShareManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: ResourceShare) -> None
  class WfWorkflowDTO(BaseDTO):
      async def from_model(cls, model: Model)
  class WfWorkflowManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: WfWorkflow) -> None
  class WfRunDTO(BaseDTO):
      async def from_model(cls, model: Model)
  class WfRunManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: WfRun) -> None
  class WfRunEventDTO(BaseDTO):
      async def from_model(cls, model: Model)
  class WfRunEventManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: WfRunEvent) -> None
  class WfStepRunDTO(BaseDTO):
      async def from_model(cls, model: Model)
  class WfStepRunManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: WfStepRun) -> None


---
Filepath: db/helpers/auto_config.py  [python]



---
Filepath: db/managers/__init__.py  [python]



---
Filepath: db/managers/resource_share.py  [python]

  class ResourceShareView(ModelView[ResourceShare]):
  class ResourceShareDTO(BaseDTO[ResourceShare]):
      async def _initialize_dto(self, model: ResourceShare) -> None
      async def _process_core_data(self, model: ResourceShare) -> None
      async def _process_metadata(self, model: ResourceShare) -> None
      async def _initial_validation(self, model: ResourceShare) -> None
      async def _final_validation(self) -> bool
      async def get_validated_dict(self) -> dict[str, Any]
  class ResourceShareBase(BaseManager[ResourceShare]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None) -> None
      def _initialize_manager(self) -> None
      async def _initialize_runtime_data(self, item: ResourceShare) -> None
      async def create_resource_share(self, **data: Any) -> ResourceShare
      async def delete_resource_share(self, id: Any) -> bool
      async def get_resource_share_with_all_related(self, id: Any) -> tuple[ResourceShare, Any]
      async def load_resource_share_by_id(self, id: Any) -> ResourceShare
      async def load_resource_share(self, use_cache: bool = True, **kwargs: Any) -> ResourceShare
      async def update_resource_share(self, id: Any, **updates: Any) -> ResourceShare
      async def load_resource_shares(self, **kwargs: Any) -> list[ResourceShare]
      async def filter_resource_shares(self, **kwargs: Any) -> list[ResourceShare]
      async def get_or_create_resource_share(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> ResourceShare | None
      async def get_resource_share_with_org(self, id: Any) -> tuple[Any, Any]
      async def get_resource_shares_with_org(self) -> list[Any]
      async def get_resource_share_with_user_profile(self, id: Any) -> tuple[Any, Any]
      async def get_resource_shares_with_user_profile(self) -> list[Any]
      async def load_resource_shares_by_org_id(self, org_id: Any) -> list[Any]
      async def filter_resource_shares_by_org_id(self, org_id: Any) -> list[Any]
      async def load_resource_shares_by_shared_with_org_id(self, shared_with_org_id: Any) -> list[Any]
      async def filter_resource_shares_by_shared_with_org_id(self, shared_with_org_id: Any) -> list[Any]
      async def load_resource_shares_by_shared_with_user_id(self, shared_with_user_id: Any) -> list[Any]
      async def filter_resource_shares_by_shared_with_user_id(self, shared_with_user_id: Any) -> list[Any]
      async def load_resource_shares_by_created_by(self, created_by: Any) -> list[Any]
      async def filter_resource_shares_by_created_by(self, created_by: Any) -> list[Any]
      async def load_resource_shares_by_ids(self, ids: list[Any]) -> list[Any]
      def add_computed_field(self, field: str) -> None
      def add_relation_field(self, field: str) -> None
      def active_resource_share_ids(self) -> set[Any]
  class ResourceShareManager(ResourceShareBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> ResourceShareManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: ResourceShare) -> None


---
Filepath: db/managers/wf_step_run.py  [python]

  class WfStepRunView(ModelView[WfStepRun]):
  class WfStepRunDTO(BaseDTO[WfStepRun]):
      async def _initialize_dto(self, model: WfStepRun) -> None
      async def _process_core_data(self, model: WfStepRun) -> None
      async def _process_metadata(self, model: WfStepRun) -> None
      async def _initial_validation(self, model: WfStepRun) -> None
      async def _final_validation(self) -> bool
      async def get_validated_dict(self) -> dict[str, Any]
  class WfStepRunBase(BaseManager[WfStepRun]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None) -> None
      def _initialize_manager(self) -> None
      async def _initialize_runtime_data(self, item: WfStepRun) -> None
      async def create_wf_step_run(self, **data: Any) -> WfStepRun
      async def delete_wf_step_run(self, id: Any) -> bool
      async def get_wf_step_run_with_all_related(self, id: Any) -> tuple[WfStepRun, Any]
      async def load_wf_step_run_by_id(self, id: Any) -> WfStepRun
      async def load_wf_step_run(self, use_cache: bool = True, **kwargs: Any) -> WfStepRun
      async def update_wf_step_run(self, id: Any, **updates: Any) -> WfStepRun
      async def load_wf_step_runs(self, **kwargs: Any) -> list[WfStepRun]
      async def filter_wf_step_runs(self, **kwargs: Any) -> list[WfStepRun]
      async def get_or_create_wf_step_run(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> WfStepRun | None
      async def get_wf_step_run_with_org(self, id: Any) -> tuple[Any, Any]
      async def get_wf_step_runs_with_org(self) -> list[Any]
      async def get_wf_step_run_with_user_profile(self, id: Any) -> tuple[Any, Any]
      async def get_wf_step_runs_with_user_profile(self) -> list[Any]
      async def get_wf_step_run_with_wf_run(self, id: Any) -> tuple[Any, Any]
      async def get_wf_step_runs_with_wf_run(self) -> list[Any]
      async def load_wf_step_runs_by_org_id(self, org_id: Any) -> list[Any]
      async def filter_wf_step_runs_by_org_id(self, org_id: Any) -> list[Any]
      async def load_wf_step_runs_by_user_id(self, user_id: Any) -> list[Any]
      async def filter_wf_step_runs_by_user_id(self, user_id: Any) -> list[Any]
      async def load_wf_step_runs_by_run_id(self, run_id: Any) -> list[Any]
      async def filter_wf_step_runs_by_run_id(self, run_id: Any) -> list[Any]
      async def load_wf_step_runs_by_ids(self, ids: list[Any]) -> list[Any]
      def add_computed_field(self, field: str) -> None
      def add_relation_field(self, field: str) -> None
      def active_wf_step_run_ids(self) -> set[Any]
  class WfStepRunManager(WfStepRunBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> WfStepRunManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: WfStepRun) -> None


---
Filepath: db/managers/wf_run_event.py  [python]

  class WfRunEventView(ModelView[WfRunEvent]):
  class WfRunEventDTO(BaseDTO[WfRunEvent]):
      async def _initialize_dto(self, model: WfRunEvent) -> None
      async def _process_core_data(self, model: WfRunEvent) -> None
      async def _process_metadata(self, model: WfRunEvent) -> None
      async def _initial_validation(self, model: WfRunEvent) -> None
      async def _final_validation(self) -> bool
      async def get_validated_dict(self) -> dict[str, Any]
  class WfRunEventBase(BaseManager[WfRunEvent]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None) -> None
      def _initialize_manager(self) -> None
      async def _initialize_runtime_data(self, item: WfRunEvent) -> None
      async def create_wf_run_event(self, **data: Any) -> WfRunEvent
      async def delete_wf_run_event(self, id: Any) -> bool
      async def get_wf_run_event_with_all_related(self, id: Any) -> tuple[WfRunEvent, Any]
      async def load_wf_run_event_by_id(self, id: Any) -> WfRunEvent
      async def load_wf_run_event(self, use_cache: bool = True, **kwargs: Any) -> WfRunEvent
      async def update_wf_run_event(self, id: Any, **updates: Any) -> WfRunEvent
      async def load_wf_run_events(self, **kwargs: Any) -> list[WfRunEvent]
      async def filter_wf_run_events(self, **kwargs: Any) -> list[WfRunEvent]
      async def get_or_create_wf_run_event(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> WfRunEvent | None
      async def get_wf_run_event_with_org(self, id: Any) -> tuple[Any, Any]
      async def get_wf_run_events_with_org(self) -> list[Any]
      async def get_wf_run_event_with_user_profile(self, id: Any) -> tuple[Any, Any]
      async def get_wf_run_events_with_user_profile(self) -> list[Any]
      async def get_wf_run_event_with_wf_run(self, id: Any) -> tuple[Any, Any]
      async def get_wf_run_events_with_wf_run(self) -> list[Any]
      async def load_wf_run_events_by_org_id(self, org_id: Any) -> list[Any]
      async def filter_wf_run_events_by_org_id(self, org_id: Any) -> list[Any]
      async def load_wf_run_events_by_user_id(self, user_id: Any) -> list[Any]
      async def filter_wf_run_events_by_user_id(self, user_id: Any) -> list[Any]
      async def load_wf_run_events_by_run_id(self, run_id: Any) -> list[Any]
      async def filter_wf_run_events_by_run_id(self, run_id: Any) -> list[Any]
      async def load_wf_run_events_by_ids(self, ids: list[Any]) -> list[Any]
      def add_computed_field(self, field: str) -> None
      def add_relation_field(self, field: str) -> None
      def active_wf_run_event_ids(self) -> set[Any]
  class WfRunEventManager(WfRunEventBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> WfRunEventManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: WfRunEvent) -> None


---
Filepath: db/managers/org.py  [python]

  class OrgView(ModelView[Org]):
  class OrgDTO(BaseDTO[Org]):
      async def _initialize_dto(self, model: Org) -> None
      async def _process_core_data(self, model: Org) -> None
      async def _process_metadata(self, model: Org) -> None
      async def _initial_validation(self, model: Org) -> None
      async def _final_validation(self) -> bool
      async def get_validated_dict(self) -> dict[str, Any]
  class OrgBase(BaseManager[Org]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None) -> None
      def _initialize_manager(self) -> None
      async def _initialize_runtime_data(self, item: Org) -> None
      async def create_org(self, **data: Any) -> Org
      async def delete_org(self, id: Any) -> bool
      async def get_org_with_all_related(self, id: Any) -> tuple[Org, Any]
      async def load_org_by_id(self, id: Any) -> Org
      async def load_org(self, use_cache: bool = True, **kwargs: Any) -> Org
      async def update_org(self, id: Any, **updates: Any) -> Org
      async def load_orgs(self, **kwargs: Any) -> list[Org]
      async def filter_orgs(self, **kwargs: Any) -> list[Org]
      async def get_or_create_org(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> Org | None
      async def get_org_with_org_member(self, id: Any) -> tuple[Any, Any]
      async def get_orgs_with_org_member(self) -> list[Any]
      async def get_org_with_wf_workflow(self, id: Any) -> tuple[Any, Any]
      async def get_orgs_with_wf_workflow(self) -> list[Any]
      async def get_org_with_wf_run(self, id: Any) -> tuple[Any, Any]
      async def get_orgs_with_wf_run(self) -> list[Any]
      async def get_org_with_wf_step_run(self, id: Any) -> tuple[Any, Any]
      async def get_orgs_with_wf_step_run(self) -> list[Any]
      async def get_org_with_wf_run_event(self, id: Any) -> tuple[Any, Any]
      async def get_orgs_with_wf_run_event(self) -> list[Any]
      async def get_org_with_resource_share(self, id: Any) -> tuple[Any, Any]
      async def get_orgs_with_resource_share(self) -> list[Any]
      async def load_orgs_by_ids(self, ids: list[Any]) -> list[Any]
      def add_computed_field(self, field: str) -> None
      def add_relation_field(self, field: str) -> None
      def active_org_ids(self) -> set[Any]
  class OrgManager(OrgBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> OrgManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: Org) -> None


---
Filepath: db/managers/org_member.py  [python]

  class OrgMemberView(ModelView[OrgMember]):
  class OrgMemberDTO(BaseDTO[OrgMember]):
      async def _initialize_dto(self, model: OrgMember) -> None
      async def _process_core_data(self, model: OrgMember) -> None
      async def _process_metadata(self, model: OrgMember) -> None
      async def _initial_validation(self, model: OrgMember) -> None
      async def _final_validation(self) -> bool
      async def get_validated_dict(self) -> dict[str, Any]
  class OrgMemberBase(BaseManager[OrgMember]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None) -> None
      def _initialize_manager(self) -> None
      async def _initialize_runtime_data(self, item: OrgMember) -> None
      async def create_org_member(self, **data: Any) -> OrgMember
      async def delete_org_member(self, id: Any) -> bool
      async def get_org_member_with_all_related(self, id: Any) -> tuple[OrgMember, Any]
      async def load_org_member_by_id(self, id: Any) -> OrgMember
      async def load_org_member(self, use_cache: bool = True, **kwargs: Any) -> OrgMember
      async def update_org_member(self, id: Any, **updates: Any) -> OrgMember
      async def load_org_members(self, **kwargs: Any) -> list[OrgMember]
      async def filter_org_members(self, **kwargs: Any) -> list[OrgMember]
      async def get_or_create_org_member(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> OrgMember | None
      async def get_org_member_with_org(self, id: Any) -> tuple[Any, Any]
      async def get_org_members_with_org(self) -> list[Any]
      async def get_org_member_with_user_profile(self, id: Any) -> tuple[Any, Any]
      async def get_org_members_with_user_profile(self) -> list[Any]
      async def load_org_members_by_org_id(self, org_id: Any) -> list[Any]
      async def filter_org_members_by_org_id(self, org_id: Any) -> list[Any]
      async def load_org_members_by_user_id(self, user_id: Any) -> list[Any]
      async def filter_org_members_by_user_id(self, user_id: Any) -> list[Any]
      async def load_org_members_by_ids(self, ids: list[Any]) -> list[Any]
      def add_computed_field(self, field: str) -> None
      def add_relation_field(self, field: str) -> None
      def active_org_member_ids(self) -> set[Any]
  class OrgMemberManager(OrgMemberBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> OrgMemberManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: OrgMember) -> None


---
Filepath: db/managers/wf_run.py  [python]

  class WfRunView(ModelView[WfRun]):
  class WfRunDTO(BaseDTO[WfRun]):
      async def _initialize_dto(self, model: WfRun) -> None
      async def _process_core_data(self, model: WfRun) -> None
      async def _process_metadata(self, model: WfRun) -> None
      async def _initial_validation(self, model: WfRun) -> None
      async def _final_validation(self) -> bool
      async def get_validated_dict(self) -> dict[str, Any]
  class WfRunBase(BaseManager[WfRun]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None) -> None
      def _initialize_manager(self) -> None
      async def _initialize_runtime_data(self, item: WfRun) -> None
      async def create_wf_run(self, **data: Any) -> WfRun
      async def delete_wf_run(self, id: Any) -> bool
      async def get_wf_run_with_all_related(self, id: Any) -> tuple[WfRun, Any]
      async def load_wf_run_by_id(self, id: Any) -> WfRun
      async def load_wf_run(self, use_cache: bool = True, **kwargs: Any) -> WfRun
      async def update_wf_run(self, id: Any, **updates: Any) -> WfRun
      async def load_wf_runs(self, **kwargs: Any) -> list[WfRun]
      async def filter_wf_runs(self, **kwargs: Any) -> list[WfRun]
      async def get_or_create_wf_run(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> WfRun | None
      async def get_wf_run_with_org(self, id: Any) -> tuple[Any, Any]
      async def get_wf_runs_with_org(self) -> list[Any]
      async def get_wf_run_with_user_profile(self, id: Any) -> tuple[Any, Any]
      async def get_wf_runs_with_user_profile(self) -> list[Any]
      async def get_wf_run_with_wf_workflow(self, id: Any) -> tuple[Any, Any]
      async def get_wf_runs_with_wf_workflow(self) -> list[Any]
      async def get_wf_run_with_wf_step_run(self, id: Any) -> tuple[Any, Any]
      async def get_wf_runs_with_wf_step_run(self) -> list[Any]
      async def get_wf_run_with_wf_run_event(self, id: Any) -> tuple[Any, Any]
      async def get_wf_runs_with_wf_run_event(self) -> list[Any]
      async def load_wf_runs_by_org_id(self, org_id: Any) -> list[Any]
      async def filter_wf_runs_by_org_id(self, org_id: Any) -> list[Any]
      async def load_wf_runs_by_user_id(self, user_id: Any) -> list[Any]
      async def filter_wf_runs_by_user_id(self, user_id: Any) -> list[Any]
      async def load_wf_runs_by_workflow_id(self, workflow_id: Any) -> list[Any]
      async def filter_wf_runs_by_workflow_id(self, workflow_id: Any) -> list[Any]
      async def load_wf_runs_by_ids(self, ids: list[Any]) -> list[Any]
      def add_computed_field(self, field: str) -> None
      def add_relation_field(self, field: str) -> None
      def active_wf_run_ids(self) -> set[Any]
  class WfRunManager(WfRunBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> WfRunManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: WfRun) -> None


---
Filepath: db/managers/wf_workflow.py  [python]

  class WfWorkflowView(ModelView[WfWorkflow]):
  class WfWorkflowDTO(BaseDTO[WfWorkflow]):
      async def _initialize_dto(self, model: WfWorkflow) -> None
      async def _process_core_data(self, model: WfWorkflow) -> None
      async def _process_metadata(self, model: WfWorkflow) -> None
      async def _initial_validation(self, model: WfWorkflow) -> None
      async def _final_validation(self) -> bool
      async def get_validated_dict(self) -> dict[str, Any]
  class WfWorkflowBase(BaseManager[WfWorkflow]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None) -> None
      def _initialize_manager(self) -> None
      async def _initialize_runtime_data(self, item: WfWorkflow) -> None
      async def create_wf_workflow(self, **data: Any) -> WfWorkflow
      async def delete_wf_workflow(self, id: Any) -> bool
      async def get_wf_workflow_with_all_related(self, id: Any) -> tuple[WfWorkflow, Any]
      async def load_wf_workflow_by_id(self, id: Any) -> WfWorkflow
      async def load_wf_workflow(self, use_cache: bool = True, **kwargs: Any) -> WfWorkflow
      async def update_wf_workflow(self, id: Any, **updates: Any) -> WfWorkflow
      async def load_wf_workflows(self, **kwargs: Any) -> list[WfWorkflow]
      async def filter_wf_workflows(self, **kwargs: Any) -> list[WfWorkflow]
      async def get_or_create_wf_workflow(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> WfWorkflow | None
      async def get_wf_workflow_with_org(self, id: Any) -> tuple[Any, Any]
      async def get_wf_workflows_with_org(self) -> list[Any]
      async def get_wf_workflow_with_user_profile(self, id: Any) -> tuple[Any, Any]
      async def get_wf_workflows_with_user_profile(self) -> list[Any]
      async def get_wf_workflow_with_wf_run(self, id: Any) -> tuple[Any, Any]
      async def get_wf_workflows_with_wf_run(self) -> list[Any]
      async def load_wf_workflows_by_org_id(self, org_id: Any) -> list[Any]
      async def filter_wf_workflows_by_org_id(self, org_id: Any) -> list[Any]
      async def load_wf_workflows_by_user_id(self, user_id: Any) -> list[Any]
      async def filter_wf_workflows_by_user_id(self, user_id: Any) -> list[Any]
      async def load_wf_workflows_by_ids(self, ids: list[Any]) -> list[Any]
      def add_computed_field(self, field: str) -> None
      def add_relation_field(self, field: str) -> None
      def active_wf_workflow_ids(self) -> set[Any]
  class WfWorkflowManager(WfWorkflowBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> WfWorkflowManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: WfWorkflow) -> None


---
Filepath: db/managers/user_profile.py  [python]

  class UserProfileView(ModelView[UserProfile]):
  class UserProfileDTO(BaseDTO[UserProfile]):
      async def _initialize_dto(self, model: UserProfile) -> None
      async def _process_core_data(self, model: UserProfile) -> None
      async def _process_metadata(self, model: UserProfile) -> None
      async def _initial_validation(self, model: UserProfile) -> None
      async def _final_validation(self) -> bool
      async def get_validated_dict(self) -> dict[str, Any]
  class UserProfileBase(BaseManager[UserProfile]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None) -> None
      def _initialize_manager(self) -> None
      async def _initialize_runtime_data(self, item: UserProfile) -> None
      async def create_user_profile(self, **data: Any) -> UserProfile
      async def delete_user_profile(self, id: Any) -> bool
      async def get_user_profile_with_all_related(self, id: Any) -> tuple[UserProfile, Any]
      async def load_user_profile_by_id(self, id: Any) -> UserProfile
      async def load_user_profile(self, use_cache: bool = True, **kwargs: Any) -> UserProfile
      async def update_user_profile(self, id: Any, **updates: Any) -> UserProfile
      async def load_user_profiles(self, **kwargs: Any) -> list[UserProfile]
      async def filter_user_profiles(self, **kwargs: Any) -> list[UserProfile]
      async def get_or_create_user_profile(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> UserProfile | None
      async def get_user_profile_with_org_member(self, id: Any) -> tuple[Any, Any]
      async def get_user_profiles_with_org_member(self) -> list[Any]
      async def get_user_profile_with_wf_workflow(self, id: Any) -> tuple[Any, Any]
      async def get_user_profiles_with_wf_workflow(self) -> list[Any]
      async def get_user_profile_with_wf_run(self, id: Any) -> tuple[Any, Any]
      async def get_user_profiles_with_wf_run(self) -> list[Any]
      async def get_user_profile_with_wf_step_run(self, id: Any) -> tuple[Any, Any]
      async def get_user_profiles_with_wf_step_run(self) -> list[Any]
      async def get_user_profile_with_wf_run_event(self, id: Any) -> tuple[Any, Any]
      async def get_user_profiles_with_wf_run_event(self) -> list[Any]
      async def get_user_profile_with_resource_share(self, id: Any) -> tuple[Any, Any]
      async def get_user_profiles_with_resource_share(self) -> list[Any]
      async def load_user_profiles_by_ids(self, ids: list[Any]) -> list[Any]
      def add_computed_field(self, field: str) -> None
      def add_relation_field(self, field: str) -> None
      def active_user_profile_ids(self) -> set[Any]
  class UserProfileManager(UserProfileBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> UserProfileManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: UserProfile) -> None


---
Filepath: db/custom/__init__.py  [python]



---
Filepath: db/custom/user.py  [python]

  class OrgMemberManager(OrgMemberBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> OrgMemberManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: OrgMember) -> None
  class OrgManager(OrgBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> OrgManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: Org) -> None
  class ResourceShareManager(ResourceShareBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> ResourceShareManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: ResourceShare) -> None
  class UserProfileManager(UserProfileBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> UserProfileManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: UserProfile) -> None
  class WfUsers:
      def __init__(self) -> None
      async def get_user(self, user_id: str) -> UserProfile
      async def update_user(self, user_id: str, updates: dict[str, Any]) -> UserProfile
      async def get_org(self, org_id: str) -> Org
      async def get_org_member(self, org_member_id: str) -> OrgMember
      async def get_resource_share(self, resource_share_id: str) -> ResourceShare
      async def get_users(self, filters: dict[str, Any]) -> list[UserProfile]
      async def get_orgs(self, filters: dict[str, Any]) -> list[Org]
      async def get_org_members(self, filters: dict[str, Any]) -> list[OrgMember]
      async def get_resource_shares(self, filters: dict[str, Any]) -> list[ResourceShare]


---
Filepath: db/custom/core.py  [python]

  class WfRunEventManager(WfRunEventBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> WfRunEventManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: WfRunEvent) -> None
  class WfRunManager(WfRunBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> WfRunManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: WfRun) -> None
  class WfStepRunManager(WfStepRunBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> WfStepRunManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: WfStepRun) -> None
  class WfWorkflowManager(WfWorkflowBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> WfWorkflowManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: WfWorkflow) -> None
  class WfCore:
      def __init__(self) -> None
      async def get_workflow(self, workflow_id: str) -> WfWorkflow
      async def get_workflows(self, filters: dict[str, Any]) -> list[WfWorkflow]
      async def create_workflow(self, workflow: WorkflowCreate) -> WorkflowResponse
      async def update_workflow(self, workflow_id: str, updates: WorkflowUpdate) -> WorkflowResponse
      async def delete_workflow(self, workflow_id: str) -> bool
      async def get_step_run(self, step_run_id: str) -> WfStepRun
      async def get_step_runs(self, filters: dict[str, Any]) -> list[WfStepRun]
      async def create_step_run(self, data: dict[str, Any]) -> WfStepRun
      async def update_step_run(self, step_run_id: str, updates: dict[str, Any]) -> WfStepRun
      async def delete_step_run(self, step_run_id: str) -> bool
      async def get_run(self, run_id: str) -> RunResponse
      async def get_runs(self, filters: dict[str, Any]) -> list[RunResponse]
      async def create_run(self, data: dict[str, Any]) -> RunResponse
      async def update_run(self, run_id: str, updates: dict[str, Any]) -> RunResponse
      async def delete_run(self, run_id: str) -> bool
      async def get_run_event(self, run_event_id: str) -> RunEventResponse
      async def get_run_events(self, filters: dict[str, Any]) -> list[RunEventResponse]
      async def create_run_event(self, run_id: str, event_type: str, step_id: str | None, payload: dict[str, Any], kwargs: dict[str, Any] = {}) -> RunEventResponse
      async def update_run_event(self, run_event_id: str, updates: dict[str, Any]) -> RunEventResponse
      async def delete_run_event(self, run_event_id: str) -> bool
      async def list_runs(self, workflow_id: str | None = None, run_status: str | None = None) -> list[RunResponse]
      async def get_step_runs_for_run(self, run_id: str) -> list[StepRunResponse]
      async def list_workflows_for_user(self, user_id: str) -> list[WorkflowResponse]
      async def list_workflows_for_org(self, org_id: str) -> list[WorkflowResponse]
```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** app, matrx_orm, matrx_utils
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "db",
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
