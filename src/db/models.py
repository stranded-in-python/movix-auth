from datetime import datetime
from typing import Any, ClassVar, Protocol, TypeVar
from uuid import UUID

import core.exceptions as ex

ID = TypeVar("ID", bound=UUID)


class UserProtocol(Protocol):
    """User protocol that ORM model should follow."""

    id: ClassVar[UUID]
    username: ClassVar[str]
    email: ClassVar[str]
    first_name: ClassVar[str]
    last_name: ClassVar[str]
    hashed_password: ClassVar[str]
    is_active: ClassVar[bool]
    is_superuser: ClassVar[bool]

    def __init__(self, *args, **kwargs) -> None:
        ...


UP = TypeVar("UP", bound=UserProtocol)


class RoleProtocol(Protocol):
    """Role protocol that ORM model should follow."""

    id: ClassVar[UUID]
    name: ClassVar[str]

    def __init__(self, *args, **kwargs) -> None:
        ...


RP = TypeVar("RP", bound=RoleProtocol)


class UserRoleProtocol(Protocol):
    """User/Role protocol that ORM model should follow."""

    id: ClassVar[UUID]
    user_id: ClassVar[UUID]
    role_id: ClassVar[UUID]


URP = TypeVar("URP", bound=UserRoleProtocol)


class UserRoleUpdateProtocol(Protocol):
    user_id: ClassVar[UUID]
    role_id: ClassVar[UUID]


URUP = TypeVar("URUP", bound=UserRoleUpdateProtocol)


class AccessRightProtocol(Protocol):
    """Access right protocol that ORM model should follow."""

    id: ClassVar[UUID]
    name: ClassVar[str]

    def __init__(self, *args, **kwargs) -> None:
        ...


ARP = TypeVar("ARP", bound=AccessRightProtocol)


class RoleAccessRightProtocol(Protocol):
    """Role/AccessRight protocol that ORM model should follow."""

    id: ClassVar[UUID]
    role_id: ClassVar[UUID]
    access_right_id: ClassVar[UUID]


RARP = TypeVar("RARP", bound=RoleAccessRightProtocol)


class SignInHistoryEvent(Protocol):
    id: ClassVar[UUID]
    user_id: ClassVar[UUID]
    timestamp: ClassVar[datetime]
    fingerprint: ClassVar[str]


SIHE = TypeVar("SIHE", bound=SignInHistoryEvent)


class AccessTokenProtocol(Protocol):
    """Access token protocol that ORM model should follow."""

    token: ClassVar[str]
    user_id: ClassVar[UUID]
    created_at: ClassVar[datetime]

    def __init__(self, *args, **kwargs) -> None:
        ...  # pragma: no cover


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
