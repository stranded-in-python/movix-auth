import typing as t

from core.dependency_types import DependencyCallable
from core.pagination import PaginateQueryParams
from models import ID, UP, RP, ARP, SIHE


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

    async def get_sign_in_history(self, user_id: ID, pagination_params: PaginateQueryParams):
        """Get recorded events in users sigh-in history"""
        raise NotImplementedError()


class BaseRoleDatabase(t.Generic[RP, ID]):
    async def get(self, role_id: ID) -> t.Optional[RP]:
        """Get a role by id."""
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


class BaseAccessRightDatabase(t.Generic[ARP, ID]):
    async def get(self, user_id: ID) -> t.Optional[UP]:
        """Get a single access right by id."""
        raise NotImplementedError()

    async def create(self, create_dict: dict[str, t.Any]) -> UP:
        """Create an access right."""
        raise NotImplementedError()

    async def update(self, user: UP, update_dict: dict[str, t.Any]) -> UP:
        """Update an access right."""
        raise NotImplementedError()

    async def delete(self, user: UP) -> None:
        """Delete an access right."""
        raise NotImplementedError()


RETURN_TYPE = t.TypeVar("RETURN_TYPE")

UserDatabaseDependency = DependencyCallable[BaseUserDatabase[UP, ID, SIHE]]
BaseRoleDatabaseDependency = DependencyCallable[BaseRoleDatabase[RP, ID]]
BaseAccessRightDatabaseDependency = DependencyCallable[BaseAccessRightDatabase[ARP, ID]]
