from __future__ import annotations

from typing import TYPE_CHECKING, Any

from app.db.managers import (
    WfRunBase,
    WfRunEventBase,
    WfStepRunBase,
    WfWorkflowBase,
)
from app.types.schemas import (
    RunEventResponse,
    RunResponse,
    StepRunResponse,
    WorkflowResponse,
)

if TYPE_CHECKING:
    from app.db.models import (
        WfRun,
        WfRunEvent,
        WfStepRun,
        WfWorkflow,
    )


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


class WfStepRunManager(WfStepRunBase):
    _instance: WfStepRunManager | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> WfStepRunManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()

    async def _initialize_runtime_data(self, item: WfStepRun) -> None:
        pass


class WfWorkflowManager(WfWorkflowBase):
    _instance: WfWorkflowManager | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> WfWorkflowManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()

    async def _initialize_runtime_data(self, item: WfWorkflow) -> None:
        pass


wf_workflow_manager_instance = WfWorkflowManager()
wf_step_run_manager_instance = WfStepRunManager()
wf_run_manager_instance = WfRunManager()
wf_run_event_manager_instance = WfRunEventManager()


class WfCore:
    def __init__(self) -> None:
        self.workflows = wf_workflow_manager_instance
        self.step_runs = wf_step_run_manager_instance
        self.runs = wf_run_manager_instance
        self.run_events = wf_run_event_manager_instance
        # Cache: run_id -> (org_id, user_id) so we don't re-fetch on every
        # step-run or event insert within a single workflow execution.
        self._run_owner_cache: dict[str, tuple[str, str]] = {}

    async def _get_run_owner(self, run_id: str) -> tuple[str, str]:
        """Return (org_id, user_id) for a run, fetching once and caching."""
        if run_id not in self._run_owner_cache:
            item = await self.runs.load_by_id(run_id)
            self._run_owner_cache[run_id] = (str(item.org_id), str(item.user_id))
        return self._run_owner_cache[run_id]

    async def get_workflow(self, workflow_id: str) -> WfWorkflow:
        return await self.workflows.load_by_id(workflow_id)

    async def get_workflow_response(self, workflow_id: str) -> WorkflowResponse | None:
        wf = await self.workflows.load_by_id(workflow_id)
        if wf is None:
            return None
        return WorkflowResponse(**wf.to_dict())

    async def get_workflows(self, filters: dict[str, Any]) -> list[WfWorkflow]:
        return await self.workflows.filter_items(**filters)

    async def get_workflow_responses(self, filters: dict[str, Any]) -> list[WorkflowResponse]:
        items = await self.workflows.filter_items(**filters)
        return [WorkflowResponse(**item.to_dict()) for item in items]

    async def create_workflow(self, **data: Any) -> WorkflowResponse:
        item = await self.workflows.create_item(**data)
        return WorkflowResponse(**item.to_dict())

    async def update_workflow(self, workflow_id: str, **updates: Any) -> WorkflowResponse:
        item = await self.workflows.update_item(workflow_id, **updates)
        return WorkflowResponse(**item.to_dict())

    async def delete_workflow(self, workflow_id: str) -> bool:
        return await self.workflows.delete_item(workflow_id)

    async def get_step_run(self, step_run_id: str) -> WfStepRun:
        return await self.step_runs.load_by_id(step_run_id)

    async def get_step_runs(self, filters: dict[str, Any]) -> list[WfStepRun]:
        return await self.step_runs.filter_items(**filters)

    async def create_step_run(self, data: dict[str, Any]) -> WfStepRun:
        if "org_id" not in data or "user_id" not in data:
            run_id = data.get("run_id")
            if run_id:
                org_id, user_id = await self._get_run_owner(str(run_id))
                data = {**data, "org_id": org_id, "user_id": user_id}
        return await self.step_runs.create_item(**data)

    async def update_step_run(self, step_run_id: str, updates: dict[str, Any]) -> WfStepRun:
        return await self.step_runs.update_item(step_run_id, **updates)

    async def delete_step_run(self, step_run_id: str) -> bool:
        return await self.step_runs.delete_item(step_run_id)

    async def get_run(self, run_id: str) -> RunResponse:
        item = await self.runs.load_by_id(run_id)
        return RunResponse(**item.to_dict())

    async def get_runs(self, filters: dict[str, Any]) -> list[RunResponse]:
        items = await self.runs.filter_items(**filters)
        return [RunResponse(**item.to_dict()) for item in items]

    async def create_run(self, data: dict[str, Any]) -> RunResponse:
        item = await self.runs.create_item(**data)
        return RunResponse(**item.to_dict())

    async def update_run(self, run_id: str, updates: dict[str, Any]) -> RunResponse:
        item = await self.runs.update_item(run_id, **updates)
        return RunResponse(**item.to_dict())

    async def delete_run(self, run_id: str) -> bool:
        return await self.runs.delete_item(run_id)

    async def get_run_event(self, run_event_id: str) -> RunEventResponse:
        item = await self.run_events.load_by_id(run_event_id)
        return RunEventResponse(**item.to_dict())

    async def get_run_events(self, filters: dict[str, Any]) -> list[RunEventResponse]:
        items = await self.run_events.filter_items(**filters)
        return [RunEventResponse(**item.to_dict()) for item in items]

    async def create_run_event(
        self,
        run_id: str,
        event_type: str,
        step_id: str | None,
        payload: dict[str, Any],
        kwargs: dict[str, Any] | None = None,
    ) -> RunEventResponse:
        org_id, user_id = await self._get_run_owner(run_id)
        data = {
            "run_id": run_id,
            "org_id": org_id,
            "user_id": user_id,
            "event_type": event_type,
            "step_id": step_id,
            "payload": payload,
            **(kwargs or {}),
        }
        item = await self.run_events.create_item(**data)
        return RunEventResponse(**item.to_dict())

    async def update_run_event(
        self, run_event_id: str, updates: dict[str, Any]
    ) -> RunEventResponse:
        item = await self.run_events.update_item(run_event_id, **updates)
        return RunEventResponse(**item.to_dict())

    async def delete_run_event(self, run_event_id: str) -> bool:
        return bool(await self.run_events.delete_item(run_event_id))

    async def list_runs(
        self, workflow_id: str | None = None, run_status: str | None = None
    ) -> list[RunResponse]:
        filters: dict[str, str] = {}
        if workflow_id:
            filters["workflow_id"] = str(workflow_id)
        if run_status:
            filters["status"] = run_status
        items = await self.runs.filter_items(**filters)
        return [RunResponse(**item.to_dict()) for item in items]

    async def get_step_runs_for_run(self, run_id: str) -> list[StepRunResponse]:
        items = await self.step_runs.filter_items(run_id=str(run_id))
        return [StepRunResponse(**item.to_dict()) for item in items]

    async def list_workflows_for_user(self, user_id: str) -> list[WorkflowResponse]:
        items = await self.workflows.filter_items(user_id=str(user_id))
        return [WorkflowResponse(**item.to_dict()) for item in items]

    async def list_workflows_for_org(self, org_id: str) -> list[WorkflowResponse]:
        items = await self.workflows.filter_items(org_id=str(org_id))
        return [WorkflowResponse(**item.to_dict()) for item in items]


wf_core = WfCore()
