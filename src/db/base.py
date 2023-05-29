import typing as t


from core.dependency_types import DependencyCallable
from core.pagination import PaginateQueryParams
from db.models import ARP, ID, RP, SIHE, UP, URP, RARP

TRow = t.TypeVar("TRow")


class BaseUserDatabase(t.Generic[UP, ID, SIHE]):
    """Base adapter for retrieving, creating and updating users from a database."""

    async def get(self, user_id: ID) -> t.Optional[UP]:
        """Get a single user by id."""
        raise NotImplementedError()

    async def get_by_username(self, email: str) -> t.Optional[UP]:
        """Get a single user by username."""
        raise NotImplementedError()

    async def get_by_email(self, email: str) -> t.Optional[UP]:
        """Get a single user by email."""
        raise NotImplementedError()

    async def create(self, create_dict: dict[str, t.Any]) -> UP:
        """Create a user."""
        raise NotImplementedError()

    async def update(self, user: UP, update_dict: dict[str, t.Any]) -> UP:
        """Update a user."""
        raise NotImplementedError()

    async def delete(self, user: UP) -> None:
        """Delete a user."""
        raise NotImplementedError()

    async def record_in_sighin_history(self, user_id: ID, event: SIHE):
        """Record in users sigh-in history"""
        raise NotImplementedError()

    async def get_sign_in_history(
        self, user_id: ID, pagination_params: PaginateQueryParams
    ) -> list[TRow]:
        """Get recorded events in users sigh-in history"""
        raise NotImplementedError()


class BaseRoleDatabase(t.Generic[RP, ID]):
    async def get_by_id(self, role_id: ID) -> t.Optional[RP]:
        """Get a role by id."""
        raise NotImplementedError()

    async def get_by_name(self, name: str) -> t.Optional[RP]:
        """Get a role by name"""
        raise NotImplementedError()

    async def create(self, create_dict: dict[str, t.Any]) -> RP:
        """Create a role."""
        raise NotImplementedError()

    async def update(self, role: RP, update_dict: dict[str, t.Any]) -> RP:
        """Update a role."""
        raise NotImplementedError()

    async def delete(self, role_id: ID) -> None:
        """Delete a role."""
        raise NotImplementedError()

    async def search(
            self,
            pagination_params: PaginateQueryParams,
            filter_param: str | None = None
    ) -> list[TRow]:
        """Delete a role."""
        raise NotImplementedError()


class BaseUserRoleDatabase(t.Generic[URP, ID]):
    async def assign_user_role(self, create_dict: dict[str, t.Any]) -> URP:
        ...

    async def get_user_role(self, user_id: ID, role_id: ID) -> URP | None:
        ...

    async def remove_user_role(self, user_role: URP) -> URP:
        ...

    async def get_user_roles(self, user_id: ID) -> list[URP]:
        ...


class BaseAccessRightDatabase(t.Generic[ARP, ID]):
    async def get(self, access_right_id: ID) -> t.Optional[ARP]:
        """Get a single access right by id."""
        raise NotImplementedError()

    async def create(self, create_dict: dict[str, t.Any]) -> ARP:
        """Create an access right."""
        raise NotImplementedError()

    async def update(self, access_right: ARP, update_dict: dict[str, t.Any]) -> ARP:
        """Update an access right."""
        raise NotImplementedError()

    async def delete(self, access_right_id: ID) -> None:
        """Delete an access right by its id."""
        raise NotImplementedError()


class BaseRoleAccessRightDatabase(t.Generic[RARP, ID]):
    async def get(self, role_id: ID, access_right_id: ID) -> t.Optional[RARP]:
        """Get a single access right by id."""
        raise NotImplementedError()

    async def create(self, create_dict: dict[str, t.Any]) -> RARP:
        """Create an access right."""
        raise NotImplementedError()

    async def update(self, role_access_right: RARP, update_dict: dict[str, t.Any]) -> RARP:
        """Update an access right."""
        raise NotImplementedError()

    async def delete(self, role_access_right: RARP) -> None:
        """Delete an access right by its id."""
        raise NotImplementedError()


class BaseRoleAccessRightDatabase(t.Generic[RARP, ID]):
    async def get(self, role_id: ID, access_right_id: ID) -> t.Optional[RARP]:
        """Get a single access right by id."""
        raise NotImplementedError()

    async def create(self, create_dict: dict[str, t.Any]) -> RARP:
        """Create an access right."""
        raise NotImplementedError()

    async def update(self, role_access_right: RARP, update_dict: dict[str, t.Any]) -> RARP:
        """Update an access right."""
        raise NotImplementedError()

    async def delete(self, role_access_right: RARP) -> None:
        """Delete an access right by its id."""
        raise NotImplementedError()


RETURN_TYPE = t.TypeVar("RETURN_TYPE")

UserDatabaseDependency = DependencyCallable[BaseUserDatabase[UP, ID, SIHE]]
BaseRoleDatabaseDependency = DependencyCallable[BaseRoleDatabase[RP, ID]]
BaseUserRoleRoleDatabaseDependency = DependencyCallable[BaseUserRoleDatabase[URP, ID]]
BaseAccessRightDatabaseDependency = DependencyCallable[BaseAccessRightDatabase[ARP, ID]]
BaseRoleAccessRightDatabaseDependency = DependencyCallable[BaseRoleAccessRightDatabase[RARP, ID]]
