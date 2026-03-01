# File: db/managers/wf_run_event.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from matrx_orm import BaseManager, BaseDTO, ModelView
from matrx_utils import vcprint

from db.models import WfRunEvent


# ---------------------------------------------------------------------------
# ModelView (new) — opt-in projection layer.
# Stores results flat on the model instance; no duplication, no nesting.
# To activate: set view_class = WfRunEventView on your manager subclass,
# or pass view_class=WfRunEventView to super().__init__().
# When active, the DTO path below is skipped automatically.
# ---------------------------------------------------------------------------

class WfRunEventView(ModelView[WfRunEvent]):
    """
    Declarative view for WfRunEvent.

    Configure what gets fetched and shaped automatically on every load:

      prefetch    — relation names to fetch concurrently (FK / IFK / M2M)
      exclude     — model field names to omit from to_dict() output
      inline_fk   — replace FK id columns with the full related object
                    e.g. {"customer_id": "customer"}

    Add async methods (no leading underscore) for computed fields:

        async def display_name(self, model: WfRunEvent) -> str:
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
class WfRunEventDTO(BaseDTO[WfRunEvent]):
    id: str

    async def _initialize_dto(self, model: WfRunEvent) -> None:
        '''Override to populate DTO fields from the model.'''
        self.id = str(model.id)
        await self._process_core_data(model)
        await self._process_metadata(model)
        await self._initial_validation(model)
        self.initialized = True

    async def _process_core_data(self, model: WfRunEvent) -> None:
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, model: WfRunEvent) -> None:
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, model: WfRunEvent) -> None:
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
#   1. Quick: set view_class = WfRunEventView  (replaces DTO automatically)
#   2. Explicit: super().__init__(WfRunEvent, view_class=WfRunEventView)
# ---------------------------------------------------------------------------

class WfRunEventBase(BaseManager[WfRunEvent]):
    view_class = None  # DTO is used by default; set to WfRunEventView to opt in

    def __init__(
        self,
        dto_class: type[Any] | None = None,
        view_class: type[Any] | None = None,
    ) -> None:
        if view_class is not None:
            self.view_class = view_class
        super().__init__(WfRunEvent, dto_class=dto_class or WfRunEventDTO)

    def _initialize_manager(self) -> None:
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: WfRunEvent) -> None:
        pass

    async def create_wf_run_event(self, **data: Any) -> WfRunEvent:
        return await self.create_item(**data)

    async def delete_wf_run_event(self, id: Any) -> bool:
        return await self.delete_item(id)

    async def get_wf_run_event_with_all_related(self, id: Any) -> tuple[WfRunEvent, Any]:
        return await self.get_item_with_all_related(id)

    async def load_wf_run_event_by_id(self, id: Any) -> WfRunEvent:
        return await self.load_by_id(id)

    async def load_wf_run_event(self, use_cache: bool = True, **kwargs: Any) -> WfRunEvent:
        return await self.load_item(use_cache, **kwargs)

    async def update_wf_run_event(self, id: Any, **updates: Any) -> WfRunEvent:
        return await self.update_item(id, **updates)

    async def load_wf_run_events(self, **kwargs: Any) -> list[WfRunEvent]:
        return await self.load_items(**kwargs)

    async def filter_wf_run_events(self, **kwargs: Any) -> list[WfRunEvent]:
        return await self.filter_items(**kwargs)

    async def get_or_create_wf_run_event(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> WfRunEvent | None:
        return await self.get_or_create(defaults, **kwargs)

    async def get_wf_run_event_with_org(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'org')

    async def get_wf_run_events_with_org(self) -> list[Any]:
        return await self.get_items_with_related('org')

    async def get_wf_run_event_with_user_profile(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'user_profile')

    async def get_wf_run_events_with_user_profile(self) -> list[Any]:
        return await self.get_items_with_related('user_profile')

    async def get_wf_run_event_with_wf_run(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'wf_run')

    async def get_wf_run_events_with_wf_run(self) -> list[Any]:
        return await self.get_items_with_related('wf_run')

    async def load_wf_run_events_by_org_id(self, org_id: Any) -> list[Any]:
        return await self.load_items(org_id=org_id)

    async def filter_wf_run_events_by_org_id(self, org_id: Any) -> list[Any]:
        return await self.filter_items(org_id=org_id)

    async def load_wf_run_events_by_user_id(self, user_id: Any) -> list[Any]:
        return await self.load_items(user_id=user_id)

    async def filter_wf_run_events_by_user_id(self, user_id: Any) -> list[Any]:
        return await self.filter_items(user_id=user_id)

    async def load_wf_run_events_by_run_id(self, run_id: Any) -> list[Any]:
        return await self.load_items(run_id=run_id)

    async def filter_wf_run_events_by_run_id(self, run_id: Any) -> list[Any]:
        return await self.filter_items(run_id=run_id)

    async def load_wf_run_events_by_ids(self, ids: list[Any]) -> list[Any]:
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field: str) -> None:
        super().add_computed_field(field)

    def add_relation_field(self, field: str) -> None:
        super().add_relation_field(field)

    @property
    def active_wf_run_event_ids(self) -> set[Any]:
        return self.active_item_ids



class WfRunEventManager(WfRunEventBase):
    _instance: WfRunEventManager | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> WfRunEventManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()

    async def _initialize_runtime_data(self, item: WfRunEvent) -> None:
        pass

wf_run_event_manager_instance = WfRunEventManager()