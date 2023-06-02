from datetime import datetime
from typing import Any, ClassVar, Protocol, TypeVar
from uuid import UUID

import core.exceptions as ex

ID = TypeVar("ID")
EmailStr = TypeVar('EmailStr')


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


UP = TypeVar("UP", bound=UserProtocol)
UC = TypeVar("UC", bound=UserCreateProtocol)


class RoleProtocol(Protocol[ID]):
    """Role protocol that ORM model should follow."""

    id: ID
    name: str


RP = TypeVar("RP", bound=RoleProtocol)


class UserRoleProtocol(Protocol[ID]):
    """User/Role protocol that ORM model should follow."""

    id: ID
    user_id: ID
    role_id: ID


URP = TypeVar("URP", bound=UserRoleProtocol)


class UserRoleUpdateProtocol(Protocol[ID]):
    user_id: ID
    role_id: ID


URUP = TypeVar("URUP", bound=UserRoleUpdateProtocol)


class AccessRightProtocol(Protocol[ID]):
    """Access right protocol that ORM model should follow."""

    id: ID
    name: str


ARP = TypeVar("ARP", bound=AccessRightProtocol)


class RoleAccessRightProtocol(Protocol[ID]):
    """Role/AccessRight protocol that ORM model should follow."""

    id: ID
    role_id: ID
    access_right_id: ID


RARP = TypeVar("RARP", bound=RoleAccessRightProtocol)


class RoleAccessRightUpdateProtocol(Protocol[ID]):
    role_id: ID
    access_right_id: ID


RARUP = TypeVar("RARUP", bound=RoleAccessRightUpdateProtocol)


class SignInHistoryEvent(Protocol[ID]):
    id: ID
    user_id: ID
    timestamp: datetime
    fingerprint: str


SIHE = TypeVar("SIHE", bound=SignInHistoryEvent)


class AccessTokenProtocol(Protocol[ID]):
    """Access token protocol that ORM model should follow."""

    token: str
    user_id: ID
    created_at: datetime


AP = TypeVar("AP", bound=AccessTokenProtocol)


class UUIDIDMixin:
    @staticmethod
    def parse_id(value: Any) -> UUID:
        if isinstance(value, UUID):
            return value
        try:
            return UUID(value)
        except ValueError as e:
            raise ex.InvalidID() from e


class IntegerIDMixin:
    @staticmethod
    def parse_id(value: Any) -> int:
        if isinstance(value, float):
            raise ex.InvalidID()
        try:
            return int(value)
        except ValueError as e:
            raise ex.InvalidID() from e
