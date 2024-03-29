import datetime
import typing as t

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from core.dependency_types import DependencyCallable
from core.pagination import PaginateQueryParams
from db.models_protocol import ARP, ID, OAP, RARP, RP, SIHE, UOAP, UP, URP

metadata_obj = MetaData(schema="users")


class SQLAlchemyBase(DeclarativeBase):
    metadata = metadata_obj


class BaseUserDatabase(t.Generic[UP, ID, SIHE, OAP, UOAP]):
    """Base adapter for retrieving, creating and updating users from a database."""

    async def get(self, user_id: ID) -> UP | None:
        """Get a single user by id."""
        raise NotImplementedError

    async def get_multiple(self, user_ids: t.Iterable[ID]) -> t.Iterable[UP] | None:
        """Get multiple users by ids."""
        raise NotImplementedError

    async def get_by_username(self, username: str) -> UP | None:
        """Get a single user by username."""
        raise NotImplementedError

    async def get_by_email(self, email: str) -> UP | None:
        """Get a single user by email."""
        raise NotImplementedError

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> UOAP | None:
        """Get a single user by OAuth account id."""
        raise NotImplementedError()

    async def create(self, create_dict: dict[str, t.Any]) -> UP:
        """Create a user."""
        raise NotImplementedError

    async def update(self, user: UP, update_dict: dict[str, t.Any]) -> UP:
        """Update a user."""
        raise NotImplementedError

    async def delete(self, user: UP) -> None:
        """Delete a user."""
        raise NotImplementedError

    async def record_in_sighin_history(self, user_id: ID, event: SIHE) -> None:
        """Record in users sigh-in history"""
        raise NotImplementedError

    async def get_sign_in_history(
        self,
        user_id: ID,
        pagination_params: PaginateQueryParams,
        since: datetime.datetime | None = None,
        to: datetime.datetime | None = None,
    ) -> t.Iterable[SIHE]:
        """Get recorded events in users sigh-in history"""
        raise NotImplementedError

    async def add_oauth_account(self, user: UP, create_dict: dict[str, t.Any]) -> UOAP:
        """Create an OAuth account and add it to the user."""
        raise NotImplementedError()

    async def update_oauth_account(
        self, user: UOAP, oauth_account: OAP, update_dict: dict[str, t.Any]
    ) -> UOAP:
        """Update an OAuth account on a user."""
        raise NotImplementedError()


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


class BaseUserRoleDatabase(t.Generic[URP, ID]):
    async def assign_user_role(self, user_id: ID, role_id: ID) -> URP:
        ...

    async def get_user_role(self, user_id: ID, role_id: ID) -> URP | None:
        ...

    async def remove_user_role(self, user_id: ID, role_id: ID) -> None:
        ...

    async def get_user_roles(self, user_id: ID) -> t.Iterable[URP]:
        ...


class BaseAccessRightDatabase(t.Generic[ARP, ID]):
    async def get(self, access_right_id: ID) -> ARP | None:
        """Get a single access right by id."""
        ...

    async def get_multiple(self, access_right_ids: t.Iterable[ID]) -> t.Iterable[ARP]:
        """Get multiple rights by ids"""
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

    async def delete(self, role_access_right_id: ID) -> None:
        """Delete an access right by its id."""
        ...

    async def remove_role_access_right(self, role_access_right: RARP) -> None:
        """Delete an access right by its id."""
        ...

    async def get_role_access_rights(self, role_id: ID) -> t.Iterable[RARP]:
        """Get rights assigned to a role"""
        ...

    async def get_roles_access_rights(
        self, role_id: t.Iterable[ID]
    ) -> t.Iterable[RARP]:
        """Get multiple rights by ids"""
        ...


RETURN_TYPE = t.TypeVar("RETURN_TYPE")

UserDatabaseDependency = DependencyCallable[BaseUserDatabase[UP, ID, SIHE, OAP, UOAP]]
BaseRoleDatabaseDependency = DependencyCallable[BaseRoleDatabase[RP, ID]]
BaseUserRoleRoleDatabaseDependency = DependencyCallable[BaseUserRoleDatabase[URP, ID]]
BaseAccessRightDatabaseDependency = DependencyCallable[BaseAccessRightDatabase[ARP, ID]]
BaseRoleAccessRightDatabaseDependency = DependencyCallable[
    BaseRoleAccessRightDatabase[RARP, ID]
]
