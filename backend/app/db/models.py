# File: db/models.py
from matrx_orm import (
    CharField,
    DateTimeField,
    ForeignKey,
    IntegerField,
    JSONBField,
    Model,
    TextField,
    UUIDField,
    model_registry,
    BaseDTO,
    BaseManager,
)
from dataclasses import dataclass
from typing import ClassVar


class Users(Model):
    id = UUIDField(primary_key=True, null=False)
    email = CharField(null=False)

    _table_name = "users"
    _db_schema = "auth"
    _database = "flow_matrx"


class Org(Model):
    id = UUIDField(primary_key=True, null=False)
    name = TextField(null=False)
    slug = TextField(null=False)
    logo_url = TextField()
    metadata = JSONBField(null=False, default={})
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    deleted_at = DateTimeField()
    _inverse_foreign_keys: ClassVar[dict[str, dict[str, str]]] = {
        "org_member": {
            "from_model": "OrgMember",
            "from_field": "org_id",
            "referenced_field": "id",
            "related_name": "org_member",
        },
        "wf_workflow": {
            "from_model": "WfWorkflow",
            "from_field": "org_id",
            "referenced_field": "id",
            "related_name": "wf_workflow",
        },
        "wf_run": {
            "from_model": "WfRun",
            "from_field": "org_id",
            "referenced_field": "id",
            "related_name": "wf_run",
        },
        "wf_step_run": {
            "from_model": "WfStepRun",
            "from_field": "org_id",
            "referenced_field": "id",
            "related_name": "wf_step_run",
        },
        "wf_run_event": {
            "from_model": "WfRunEvent",
            "from_field": "org_id",
            "referenced_field": "id",
            "related_name": "wf_run_event",
        },
        "resource_share": {
            "from_model": "ResourceShare",
            "from_field": "shared_with_org_id",
            "referenced_field": "id",
            "related_name": "resource_share",
        },
    }
    _database = "flow_matrx"


class UserProfile(Model):
    id = UUIDField(primary_key=True, null=False)
    display_name = TextField()
    email = TextField()
    avatar_url = TextField()
    metadata = JSONBField(null=False, default={})
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    deleted_at = DateTimeField()
    _inverse_foreign_keys: ClassVar[dict[str, dict[str, str]]] = {
        "org_member": {
            "from_model": "OrgMember",
            "from_field": "user_id",
            "referenced_field": "id",
            "related_name": "org_member",
        },
        "wf_workflow": {
            "from_model": "WfWorkflow",
            "from_field": "user_id",
            "referenced_field": "id",
            "related_name": "wf_workflow",
        },
        "wf_run": {
            "from_model": "WfRun",
            "from_field": "user_id",
            "referenced_field": "id",
            "related_name": "wf_run",
        },
        "wf_step_run": {
            "from_model": "WfStepRun",
            "from_field": "user_id",
            "referenced_field": "id",
            "related_name": "wf_step_run",
        },
        "wf_run_event": {
            "from_model": "WfRunEvent",
            "from_field": "user_id",
            "referenced_field": "id",
            "related_name": "wf_run_event",
        },
        "resource_share": {
            "from_model": "ResourceShare",
            "from_field": "created_by",
            "referenced_field": "id",
            "related_name": "resource_share",
        },
    }
    _database = "flow_matrx"


class OrgMember(Model):
    id = UUIDField(primary_key=True, null=False)
    org_id = ForeignKey(to_model=Org, to_column="id", null=False)
    user_id = ForeignKey(to_model=UserProfile, to_column="id", null=False)
    role = TextField(null=False, default="member")
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    deleted_at = DateTimeField()
    _inverse_foreign_keys: ClassVar[dict[str, dict[str, str]]] = {}
    _database = "flow_matrx"


class ResourceShare(Model):
    id = UUIDField(primary_key=True, null=False)
    org_id = ForeignKey(to_model=Org, to_column="id", null=False)
    resource_type = TextField(null=False)
    resource_id = UUIDField(null=False)
    share_type = TextField(null=False)
    shared_with_org_id = ForeignKey(
        to_model=Org,
        to_column="id",
    )
    shared_with_user_id = ForeignKey(
        to_model=UserProfile,
        to_column="id",
    )
    permission = TextField(null=False, default="view")
    created_by = ForeignKey(to_model=UserProfile, to_column="id", null=False)
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    deleted_at = DateTimeField()
    _inverse_foreign_keys: ClassVar[dict[str, dict[str, str]]] = {}
    _database = "flow_matrx"


class WfWorkflow(Model):
    id = UUIDField(primary_key=True, null=False)
    org_id = ForeignKey(to_model=Org, to_column="id", null=False)
    user_id = ForeignKey(to_model=UserProfile, to_column="id", null=False)
    name = TextField(null=False)
    description = TextField(null=False)
    version = IntegerField(null=False, default=1)
    status = TextField(null=False, default="draft")
    definition = JSONBField(null=False, default={"edges": [], "nodes": []})
    input_schema = JSONBField()
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    deleted_at = DateTimeField()
    _inverse_foreign_keys: ClassVar[dict[str, dict[str, str]]] = {
        "wf_run": {
            "from_model": "WfRun",
            "from_field": "workflow_id",
            "referenced_field": "id",
            "related_name": "wf_run",
        }
    }
    _database = "flow_matrx"


class WfRun(Model):
    id = UUIDField(primary_key=True, null=False)
    org_id = ForeignKey(to_model=Org, to_column="id", null=False)
    user_id = ForeignKey(to_model=UserProfile, to_column="id", null=False)
    workflow_id = ForeignKey(to_model=WfWorkflow, to_column="id", null=False)
    status = TextField(null=False, default="pending")
    trigger_type = TextField(null=False, default="manual")
    input = JSONBField(null=False, default={})
    context = JSONBField(null=False, default={})
    error = TextField()
    idempotency_key = TextField()
    started_at = DateTimeField()
    completed_at = DateTimeField()
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    deleted_at = DateTimeField()
    _inverse_foreign_keys: ClassVar[dict[str, dict[str, str]]] = {
        "wf_step_run": {
            "from_model": "WfStepRun",
            "from_field": "run_id",
            "referenced_field": "id",
            "related_name": "wf_step_run",
        },
        "wf_run_event": {
            "from_model": "WfRunEvent",
            "from_field": "run_id",
            "referenced_field": "id",
            "related_name": "wf_run_event",
        },
    }
    _database = "flow_matrx"


class WfRunEvent(Model):
    id = UUIDField(primary_key=True, null=False)
    org_id = ForeignKey(to_model=Org, to_column="id", null=False)
    user_id = ForeignKey(to_model=UserProfile, to_column="id", null=False)
    run_id = ForeignKey(to_model=WfRun, to_column="id", null=False)
    step_id = TextField()
    event_type = TextField(null=False)
    payload = JSONBField(null=False, default={})
    created_at = DateTimeField(null=False)
    _inverse_foreign_keys: ClassVar[dict[str, dict[str, str]]] = {}
    _database = "flow_matrx"


class WfStepRun(Model):
    id = UUIDField(primary_key=True, null=False)
    org_id = ForeignKey(to_model=Org, to_column="id", null=False)
    user_id = ForeignKey(to_model=UserProfile, to_column="id", null=False)
    run_id = ForeignKey(to_model=WfRun, to_column="id", null=False)
    step_id = TextField(null=False)
    step_type = TextField(null=False)
    status = TextField(null=False, default="pending")
    input = JSONBField(null=False, default={})
    output = JSONBField(null=False, default={})
    error = TextField()
    attempt = IntegerField(null=False, default=1)
    started_at = DateTimeField()
    completed_at = DateTimeField()
    created_at = DateTimeField(null=False)
    updated_at = DateTimeField(null=False)
    deleted_at = DateTimeField()
    _inverse_foreign_keys: ClassVar[dict[str, dict[str, str]]] = {}
    _database = "flow_matrx"


model_registry.register_all(
    [Org, UserProfile, OrgMember, ResourceShare, WfWorkflow, WfRun, WfRunEvent, WfStepRun, Users]
)


@dataclass
class OrgDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "Model"):
        return cls(id=str(model.id))


class OrgManager(BaseManager):
    def __init__(self):
        super().__init__(Org, OrgDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: Org) -> None:
        pass


@dataclass
class UserProfileDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "Model"):
        return cls(id=str(model.id))


class UserProfileManager(BaseManager):
    def __init__(self):
        super().__init__(UserProfile, UserProfileDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: UserProfile) -> None:
        pass


@dataclass
class OrgMemberDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "Model"):
        return cls(id=str(model.id))


class OrgMemberManager(BaseManager):
    def __init__(self):
        super().__init__(OrgMember, OrgMemberDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: OrgMember) -> None:
        pass


@dataclass
class ResourceShareDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "Model"):
        return cls(id=str(model.id))


class ResourceShareManager(BaseManager):
    def __init__(self):
        super().__init__(ResourceShare, ResourceShareDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: ResourceShare) -> None:
        pass


@dataclass
class WfWorkflowDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "Model"):
        return cls(id=str(model.id))


class WfWorkflowManager(BaseManager):
    def __init__(self):
        super().__init__(WfWorkflow, WfWorkflowDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: WfWorkflow) -> None:
        pass


@dataclass
class WfRunDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "Model"):
        return cls(id=str(model.id))


class WfRunManager(BaseManager):
    def __init__(self):
        super().__init__(WfRun, WfRunDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: WfRun) -> None:
        pass


@dataclass
class WfRunEventDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "Model"):
        return cls(id=str(model.id))


class WfRunEventManager(BaseManager):
    def __init__(self):
        super().__init__(WfRunEvent, WfRunEventDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: WfRunEvent) -> None:
        pass


@dataclass
class WfStepRunDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model: "Model"):
        return cls(id=str(model.id))


class WfStepRunManager(BaseManager):
    def __init__(self):
        super().__init__(WfStepRun, WfStepRunDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: WfStepRun) -> None:
        pass
