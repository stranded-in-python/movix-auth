from datetime import datetime
from typing import Any, Protocol, TypeVar
from uuid import UUID

import core.exceptions as ex

ID = TypeVar("ID")


class UserProtocol(Protocol[ID]):
    """User protocol that ORM model should follow."""

    id: ID
    username: str
    email: str
    first_name: str
    last_name: str
    hashed_password: str
    is_active: bool
    is_superuser: bool

    def __init__(self, *args, **kwargs) -> None:
        ...


UP = TypeVar("UP", bound=UserProtocol)


class RoleProtocol(Protocol[ID]):
    """Role protocol that ORM model should follow."""

    id: ID
    name: str

    def __init__(self, *args, **kwargs) -> None:
        ...


RP = TypeVar("RP", bound=RoleProtocol)


class UserRoleProtocol(Protocol[ID]):
    """User/Role protocol that ORM model should follow."""

    id: ID
    user_id: ID
    role_id: ID


URP = TypeVar("URP", bound=UserRoleProtocol)


class AccessRightProtocol(Protocol[ID]):
    """Access right protocol that ORM model should follow."""

    id: ID
    name: str

    def __init__(self, *args, **kwargs) -> None:
        ...


ARP = TypeVar("ARP", bound=AccessRightProtocol)


class RoleAccessRightProtocol(Protocol[ID]):
    """Role/AccessRight protocol that ORM model should follow."""

    id: ID
    user_id: ID
    access_right_id: ID


RARP = TypeVar("RARP", bound=RoleAccessRightProtocol)


class SignInHistoryEvent(Protocol[ID]):
    id: ID
    user_id: ID
    timestamp: datetime
    fingerprint: str


SIHE = TypeVar("SIHE", bound=SignInHistoryEvent)


class AccessTokenProtocol(Protocol[Protocol.ID]):
    """Access token protocol that ORM model should follow."""

    token: str
    user_id: ID
    created_at: datetime

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
