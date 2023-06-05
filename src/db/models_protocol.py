from datetime import datetime
from typing import Any, Protocol, TypeVar
from uuid import UUID

import pydantic

import core.exceptions as ex

ID = TypeVar("ID")
EmailStr = TypeVar('EmailStr')


class UUIDIDMixin:
    def parse_id(self, value: Any) -> UUID:
        if isinstance(value, UUID):
            return value
        try:
            return UUID(value)
        except ValueError as e:
            raise ex.InvalidID() from e


class IntegerIDMixin:
    def parse_id(self, value: Any) -> int:
        if isinstance(value, float):
            raise ex.InvalidID()
        try:
            return int(value)
        except ValueError as e:
            raise ex.InvalidID() from e


class UserCreateProtocol(Protocol[EmailStr]):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    is_active: bool
    is_superuser: bool


class UserProtocol(Protocol[ID, EmailStr]):
    """User protocol that ORM model should follow."""

    id: ID
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    hashed_password: str
    is_active: bool
    is_superuser: bool


UP = TypeVar("UP", bound=UserProtocol[UUID, pydantic.EmailStr])
UC = TypeVar("UC", bound=UserCreateProtocol[str])


class RoleProtocol(Protocol[ID]):
    """Role protocol that ORM model should follow."""

    id: ID
    name: str


RP = TypeVar("RP", bound=RoleProtocol[UUID])


class UserRoleProtocol(Protocol[ID]):
    """User/Role protocol that ORM model should follow."""

    id: ID
    user_id: ID
    role_id: ID


URP = TypeVar("URP", bound=UserRoleProtocol[UUID])


class UserRoleUpdateProtocol(Protocol[ID]):
    user_id: ID
    role_id: ID


URUP = TypeVar("URUP", bound=UserRoleUpdateProtocol[UUID])


class AccessRightProtocol(Protocol[ID]):
    """Access right protocol that ORM model should follow."""

    id: ID
    name: str


ARP = TypeVar("ARP", bound=AccessRightProtocol[UUID])


class RoleAccessRightProtocol(Protocol[ID]):
    """Role/AccessRight protocol that ORM model should follow."""

    id: ID
    role_id: ID
    access_right_id: ID


RARP = TypeVar("RARP", bound=RoleAccessRightProtocol[UUID])


class RoleAccessRightUpdateProtocol(Protocol[ID]):
    role_id: ID
    access_right_id: ID


RARUP = TypeVar("RARUP", bound=RoleAccessRightUpdateProtocol[UUID])


class SignInHistoryEvent(Protocol[ID]):
    id: ID
    user_id: ID
    timestamp: datetime
    fingerprint: str


SIHE = TypeVar("SIHE", bound=SignInHistoryEvent[UUID])


class AccessTokenProtocol(Protocol[ID]):
    """Access token protocol that ORM model should follow."""

    token: str
    user_id: ID
    created_at: datetime


AP = TypeVar("AP", bound=AccessTokenProtocol[UUID])
