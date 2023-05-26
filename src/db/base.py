import typing as t

from ..core.dependency_types import DependencyCallable
from ..models import ID, UP, RP, ARP

class BaseUserDatabase(t.Generic[UP, ID]):
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


class BaseRoleDatabase(t.Generic[RP, ID]):
    async def get(self, user_id: ID) -> t.Optional[UP]:
        """Get a single user by id."""
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

UserDatabaseDependency = DependencyCallable[BaseUserDatabase[UP, ID]]
BaseRoleDatabaseDependency = DependencyCallable[BaseRoleDatabase[RP, ID]]
BaseAccessRightDatabaseDependency = DependencyCallable[BaseAccessRightDatabase[ARP, ID]]
