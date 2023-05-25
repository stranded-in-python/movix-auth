from datetime import datetime
from typing import Protocol, TypeVar, Any
from uuid import UUID

from pydantic import BaseModel

import src.core.exceptions as ex

ID = TypeVar("ID")


class UserProtocol(Protocol[ID]):
    """User protocol that ORM model should follow."""

    id: ID
    email: str
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


class AccessRightProtocol(Protocol[ID]):
    """Access right protocol that ORM model should follow."""

    id: ID
    name: str
    roles: list[RP]

    def __init__(self, *args, **kwargs) -> None:
        ...


ARP = TypeVar("RP", bound=RoleProtocol)


class SignInHistoryEvent(BaseModel):
    timestamp: datetime
    ip: str
    # TODO add attrs


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
