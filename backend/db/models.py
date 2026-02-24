# File: db/models.py
from matrx_orm import (
    Model,
    UUIDField,
    CharField,
    TextField,
    IntegerField,
    JSONBField,
    DateTimeField,
    ForeignKey,
    model_registry,
    BaseDTO,
    BaseManager,
)
from dataclasses import dataclass


class Workflow(Model):
    id = UUIDField(primary_key=True, null=False)
    name = TextField(null=False)
    description = TextField(default="")
    version = IntegerField(null=False, default=1)
    status = CharField(null=False, default="draft")  # draft | published | archived
    definition = JSONBField(null=False, default={"nodes": [], "edges": []})
    input_schema = JSONBField(null=True)
    created_by = UUIDField(null=True)
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)

    _table_name = "workflows"
    _database = "flow_matrx"
    _inverse_foreign_keys = {
        "runs": {"from_model": "Run", "from_field": "workflow_id", "referenced_field": "id", "related_name": "runs"},
    }


class Run(Model):
    id = UUIDField(primary_key=True, null=False)
    workflow_id = ForeignKey(to_model=Workflow, to_column="id", null=False)
    status = CharField(null=False, default="pending")      # pending | running | paused | completed | failed | cancelled
    trigger_type = CharField(null=False, default="manual") # manual | schedule | webhook | event
    input = JSONBField(null=False, default={})
    context = JSONBField(null=False, default={})
    error = TextField(null=True)
    idempotency_key = CharField(null=True, unique=True)
    started_at = DateTimeField(null=True)
    completed_at = DateTimeField(null=True)
    created_at = DateTimeField(null=False)

    _table_name = "runs"
    _database = "flow_matrx"
    _inverse_foreign_keys = {
        "step_runs": {"from_model": "StepRun", "from_field": "run_id", "referenced_field": "id", "related_name": "step_runs"},
        "run_events": {"from_model": "RunEvent", "from_field": "run_id", "referenced_field": "id", "related_name": "run_events"},
    }


class StepRun(Model):
    id = UUIDField(primary_key=True, null=False)
    run_id = ForeignKey(to_model=Run, to_column="id", null=False)
    step_id = CharField(null=False)   # matches node id in workflow definition JSONB
    step_type = CharField(null=False) # denormalized from node definition
    status = CharField(null=False, default="pending")  # pending | running | completed | failed | skipped | waiting | cancelled
    input = JSONBField(default={})
    output = JSONBField(default={})
    error = TextField(null=True)
    attempt = IntegerField(null=False, default=1)
    started_at = DateTimeField(null=True)
    completed_at = DateTimeField(null=True)
    created_at = DateTimeField(null=False)

    _table_name = "step_runs"
    _database = "flow_matrx"
    _unique_together = [["run_id", "step_id", "attempt"]]


class RunEvent(Model):
    id = UUIDField(primary_key=True, null=False)
    run_id = ForeignKey(to_model=Run, to_column="id", null=False)
    step_id = CharField(null=True)  # NULL for run-level events
    event_type = CharField(null=False)
    payload = JSONBField(null=False, default={})
    created_at = DateTimeField(null=False)

    _table_name = "run_events"
    _database = "flow_matrx"


@dataclass
class WorkflowDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "Workflow"):
        return cls(id=str(model.id))


class WorkflowManager(BaseManager):
    def __init__(self):
        super().__init__(Workflow, WorkflowDTO)

    def _initialize_manager(self):
        super()._initialize_manager()


workflow_manager_instance = WorkflowManager()


@dataclass
class RunDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "Run"):
        return cls(id=str(model.id))


class RunManager(BaseManager):
    def __init__(self):
        super().__init__(Run, RunDTO)

    def _initialize_manager(self):
        super()._initialize_manager()


run_manager_instance = RunManager()


@dataclass
class StepRunDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "StepRun"):
        return cls(id=str(model.id))


class StepRunManager(BaseManager):
    def __init__(self):
        super().__init__(StepRun, StepRunDTO)

    def _initialize_manager(self):
        super()._initialize_manager()


step_run_manager_instance = StepRunManager()


@dataclass
class RunEventDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "RunEvent"):
        return cls(id=str(model.id))


class RunEventManager(BaseManager):
    def __init__(self):
        super().__init__(RunEvent, RunEventDTO)

    def _initialize_manager(self):
        super()._initialize_manager()


run_event_manager_instance = RunEventManager()


model_registry.register_all([
    Workflow,
    Run,
    StepRun,
    RunEvent,
])
