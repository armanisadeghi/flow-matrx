from __future__ import annotations

from typing import TYPE_CHECKING, Any

from app.db.managers import (
    OrgBase,
    OrgMemberBase,
    ResourceShareBase,
    UserProfileBase,
)

if TYPE_CHECKING:
    from app.db.models import (
        Org,
        OrgMember,
        ResourceShare,
        UserProfile,
    )


class OrgMemberManager(OrgMemberBase):
    _instance: OrgMemberManager | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> OrgMemberManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()

    async def _initialize_runtime_data(self, item: OrgMember) -> None:
        pass


class OrgManager(OrgBase):
    _instance: OrgManager | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> OrgManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()

    async def _initialize_runtime_data(self, item: Org) -> None:
        pass


class ResourceShareManager(ResourceShareBase):
    _instance: ResourceShareManager | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> ResourceShareManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()

    async def _initialize_runtime_data(self, item: ResourceShare) -> None:
        pass


class UserProfileManager(UserProfileBase):
    _instance: UserProfileManager | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> UserProfileManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()

    async def _initialize_runtime_data(self, item: UserProfile) -> None:
        pass


user_profile_manager_instance = UserProfileManager()
org_member_manager_instance = OrgMemberManager()
org_manager_instance = OrgManager()
resource_share_manager_instance = ResourceShareManager()


class WfUsers:
    def __init__(self) -> None:
        self.users = user_profile_manager_instance
        self.orgs = org_manager_instance
        self.org_members = org_member_manager_instance
        self.resource_shares = resource_share_manager_instance

    async def get_user(self, user_id: str) -> UserProfile:
        return await self.users.load_by_id(user_id)

    async def update_user(self, user_id: str, updates: dict[str, Any]) -> UserProfile:
        return await self.users.update_item(user_id, **updates)

    async def get_org(self, org_id: str) -> Org:
        return await self.orgs.load_by_id(org_id)

    async def get_org_member(self, org_member_id: str) -> OrgMember:
        return await self.org_members.load_by_id(org_member_id)

    async def get_resource_share(self, resource_share_id: str) -> ResourceShare:
        return await self.resource_shares.load_by_id(resource_share_id)

    async def get_users(self, filters: dict[str, Any]) -> list[UserProfile]:
        return await self.users.filter_items(**filters)

    async def get_orgs(self, filters: dict[str, Any]) -> list[Org]:
        return await self.orgs.filter_items(**filters)

    async def get_org_members(self, filters: dict[str, Any]) -> list[OrgMember]:
        return await self.org_members.filter_items(**filters)

    async def get_resource_shares(self, filters: dict[str, Any]) -> list[ResourceShare]:
        return await self.resource_shares.filter_items(**filters)


wf_users_instance = WfUsers()
