import typing as t

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from core.dependency_types import DependencyCallable
from core.pagination import PaginateQueryParams
from db.models import ARP, ID, RARP, RP, SIHE, UP, URP, URUP

metadata_obj = MetaData(schema="users")


class SQLAlchemyBase(DeclarativeBase):
    metadata = metadata_obj


class BaseUserDatabase(t.Generic[UP, ID, SIHE]):
    """Base adapter for retrieving, creating and updating users from a database."""

    async def get(self, user_id: ID) -> UP | None:
        """Get a single user by id."""
        ...

    async def get_by_username(self, username: str) -> UP | None:
        """Get a single user by username."""
        ...

    async def get_by_email(self, email: str) -> UP | None:
        """Get a single user by email."""
        ...

    async def create(self, create_dict: dict[str, t.Any]) -> UP:
        """Create a user."""
        ...

    async def update(self, user: UP, update_dict: dict[str, t.Any]) -> UP:
        """Update a user."""
        ...

    async def delete(self, user: UP) -> None:
        """Delete a user."""
        ...

    async def record_in_sighin_history(self, user_id: ID, event: SIHE):
        """Record in users sigh-in history"""
        ...

    async def get_sign_in_history(
        self, user_id: ID, pagination_params: PaginateQueryParams
    ) -> t.Iterable[SIHE]:
        """Get recorded events in users sigh-in history"""
        ...


class BaseRoleDatabase(t.Generic[RP, ID]):
    async def get_by_id(self, role_id: ID) -> RP | None:
        """Get a role by id."""
        ...

    async def get_by_name(self, name: str) -> RP | None:
        """Get a role by name"""
        ...

    async def create(self, create_dict: dict[str, t.Any]) -> RP:
        """Create a role."""
        ...

    async def update(self, role: RP, update_dict: dict[str, t.Any]) -> RP:
        """Update a role."""
        ...

    async def delete(self, role_id: ID) -> None:
        """Delete a role."""
        ...

    async def search(
        self, pagination_params: PaginateQueryParams, filter_param: str | None = None
    ) -> t.Iterable[RP]:
        """Delete a role."""
        ...


class BaseUserRoleDatabase(t.Generic[URP, URUP, ID]):
    async def assign_user_role(self, user_id: ID, role_id: ID) -> URP:
        ...

    async def get_user_role(self, user_id: ID, role_id: ID) -> URP | None:
        ...

    async def remove_user_role(self, user_role: URUP) -> URP:
        ...

    async def get_user_roles(self, user_id: ID) -> t.Iterable[URP]:
        ...


class BaseAccessRightDatabase(t.Generic[ARP, ID]):
    async def get(self, access_right_id: ID) -> ARP | None:
        """Get a single access right by id."""
        ...

    async def create(self, create_dict: dict[str, t.Any]) -> ARP:
        """Create an access right."""
        ...

    async def update(self, access_right: ARP, update_dict: dict[str, t.Any]) -> ARP:
        """Update an access right."""
        ...

    async def delete(self, access_right_id: ID) -> None:
        """Delete an access right by its id."""
        ...

    async def get_by_name(self, name: str) -> ARP | None:
        """Get an access by name"""
        ...

    async def search(
        self, pagination_params: PaginateQueryParams, filter_param: str | None = None
    ) -> t.Iterable[ARP]:
        """Search an access right."""
        ...


class BaseRoleAccessRightDatabase(t.Generic[RARP, ID]):
    async def get(self, role_id: ID, access_right_id: ID) -> RARP | None:
        """Get a single access right by id."""
        ...

    async def create(self, create_dict: dict[str, t.Any]) -> RARP:
        """Create an access right."""
        ...

    async def update(
        self, role_access_right: RARP, update_dict: dict[str, t.Any]
    ) -> RARP:
        """Update an access right."""
        ...

    async def delete(self, role_access_right: RARP) -> None:
        """Delete an access right by its id."""
        ...

    async def remove_role_access_right(self, role_access_right: RARP) -> None:
        """Delete an access right by its id."""
        ...

    async def get_role_access_rights(self, role_id: ID) -> t.Iterable[RARP]:
        ...


RETURN_TYPE = t.TypeVar("RETURN_TYPE")

UserDatabaseDependency = DependencyCallable[BaseUserDatabase[UP, ID, SIHE]]
BaseRoleDatabaseDependency = DependencyCallable[BaseRoleDatabase[RP, ID]]
BaseUserRoleRoleDatabaseDependency = DependencyCallable[
    BaseUserRoleDatabase[URP, URUP, ID]
]
BaseAccessRightDatabaseDependency = DependencyCallable[BaseAccessRightDatabase[ARP, ID]]
BaseRoleAccessRightDatabaseDependency = DependencyCallable[
    BaseRoleAccessRightDatabase[RARP, ID]
]
