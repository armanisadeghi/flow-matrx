# File: db/managers/wf_run.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from matrx_orm import BaseDTO, BaseManager, ModelView
from matrx_utils import vcprint

from ..models import WfRun

# ---------------------------------------------------------------------------
# ModelView (new) — opt-in projection layer.
# Stores results flat on the model instance; no duplication, no nesting.
# To activate: set view_class = WfRunView on your manager subclass,
# or pass view_class=WfRunView to super().__init__().
# When active, the DTO path below is skipped automatically.
# ---------------------------------------------------------------------------

class WfRunView(ModelView[WfRun]):
    """
    Declarative view for WfRun.

    Configure what gets fetched and shaped automatically on every load:

      prefetch    — relation names to fetch concurrently (FK / IFK / M2M)
      exclude     — model field names to omit from to_dict() output
      inline_fk   — replace FK id columns with the full related object
                    e.g. {"customer_id": "customer"}

    Add async methods (no leading underscore) for computed fields:

        async def display_name(self, model: WfRun) -> str:
            return model.name.title()
    """

    prefetch: list[str] = []
    exclude: list[str] = []
    inline_fk: dict[str, str] = {}

    # ------------------------------------------------------------------ #
    # Computed fields — add async methods below.                          #
    # Each method receives the model instance and returns a plain value.  #
    # Errors in computed fields are logged and stored as None —           #
    # they never abort the load.                                          #
    # ------------------------------------------------------------------ #


# ---------------------------------------------------------------------------
# BaseDTO (default) — active by default, fully backward compatible.
# Extend _process_core_data / _process_metadata with your business logic.
# When you are ready to migrate to the View above, set view_class on your
# manager subclass and this DTO will be bypassed automatically.
# ---------------------------------------------------------------------------

@dataclass
class WfRunDTO(BaseDTO[WfRun]):
    id: str

    async def _initialize_dto(self, model: WfRun) -> None:
        '''Override to populate DTO fields from the model.'''
        self.id = str(model.id)
        await self._process_core_data(model)
        await self._process_metadata(model)
        await self._initial_validation(model)
        self.initialized = True

    async def _process_core_data(self, model: WfRun) -> None:
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, model: WfRun) -> None:
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, model: WfRun) -> None:
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self) -> bool:
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self) -> dict[str, Any]:
        '''Get the validated dictionary.'''
        await self._final_validation()
        return self.to_dict()


# ---------------------------------------------------------------------------
# Manager — DTO is active by default for full backward compatibility.
# To switch to the View (opt-in):
#   1. Quick: set view_class = WfRunView  (replaces DTO automatically)
#   2. Explicit: super().__init__(WfRun, view_class=WfRunView)
# ---------------------------------------------------------------------------

class WfRunBase(BaseManager[WfRun]):
    view_class = None  # DTO is used by default; set to WfRunView to opt in

    def __init__(
        self,
        dto_class: type[Any] | None = None,
        view_class: type[Any] | None = None,
    ) -> None:
        if view_class is not None:
            self.view_class = view_class
        super().__init__(WfRun, dto_class=dto_class or WfRunDTO)

    def _initialize_manager(self) -> None:
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: WfRun) -> None:
        pass

    async def create_wf_run(self, **data: Any) -> WfRun:
        return await self.create_item(**data)

    async def delete_wf_run(self, id: Any) -> bool:
        return await self.delete_item(id)

    async def get_wf_run_with_all_related(self, id: Any) -> tuple[WfRun, Any]:
        return await self.get_item_with_all_related(id)

    async def load_wf_run_by_id(self, id: Any) -> WfRun:
        return await self.load_by_id(id)

    async def load_wf_run(self, use_cache: bool = True, **kwargs: Any) -> WfRun:
        return await self.load_item(use_cache, **kwargs)

    async def update_wf_run(self, id: Any, **updates: Any) -> WfRun:
        return await self.update_item(id, **updates)

    async def load_wf_runs(self, **kwargs: Any) -> list[WfRun]:
        return await self.load_items(**kwargs)

    async def filter_wf_runs(self, **kwargs: Any) -> list[WfRun]:
        return await self.filter_items(**kwargs)

    async def get_or_create_wf_run(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> WfRun | None:
        return await self.get_or_create(defaults, **kwargs)

    async def get_wf_run_with_org(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'org')

    async def get_wf_runs_with_org(self) -> list[Any]:
        return await self.get_items_with_related('org')

    async def get_wf_run_with_user_profile(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'user_profile')

    async def get_wf_runs_with_user_profile(self) -> list[Any]:
        return await self.get_items_with_related('user_profile')

    async def get_wf_run_with_wf_workflow(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'wf_workflow')

    async def get_wf_runs_with_wf_workflow(self) -> list[Any]:
        return await self.get_items_with_related('wf_workflow')

    async def get_wf_run_with_wf_step_run(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'wf_step_run')

    async def get_wf_runs_with_wf_step_run(self) -> list[Any]:
        return await self.get_items_with_related('wf_step_run')

    async def get_wf_run_with_wf_run_event(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'wf_run_event')

    async def get_wf_runs_with_wf_run_event(self) -> list[Any]:
        return await self.get_items_with_related('wf_run_event')

    async def load_wf_runs_by_org_id(self, org_id: Any) -> list[Any]:
        return await self.load_items(org_id=org_id)

    async def filter_wf_runs_by_org_id(self, org_id: Any) -> list[Any]:
        return await self.filter_items(org_id=org_id)

    async def load_wf_runs_by_user_id(self, user_id: Any) -> list[Any]:
        return await self.load_items(user_id=user_id)

    async def filter_wf_runs_by_user_id(self, user_id: Any) -> list[Any]:
        return await self.filter_items(user_id=user_id)

    async def load_wf_runs_by_workflow_id(self, workflow_id: Any) -> list[Any]:
        return await self.load_items(workflow_id=workflow_id)

    async def filter_wf_runs_by_workflow_id(self, workflow_id: Any) -> list[Any]:
        return await self.filter_items(workflow_id=workflow_id)

    async def load_wf_runs_by_ids(self, ids: list[Any]) -> list[Any]:
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field: str) -> None:
        super().add_computed_field(field)

    def add_relation_field(self, field: str) -> None:
        super().add_relation_field(field)

    @property
    def active_wf_run_ids(self) -> set[Any]:
        return self.active_item_ids



class WfRunManager(WfRunBase):
    _instance: WfRunManager | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> WfRunManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()

    async def _initialize_runtime_data(self, item: WfRun) -> None:
        pass

wf_run_manager_instance = WfRunManager()
