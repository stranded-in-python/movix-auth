from datetime import datetime
from typing import Protocol, TypeVar, Any
from uuid import UUID

from pydantic import BaseModel

import core.exceptions as ex

ID = TypeVar("ID")


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str


class UserDetailed(BaseModel):
    id: UUID
    username: str
    email: str
    first_name: str
    last_name: str


class UserPayload(BaseModel):
    id: UUID | str
    refresh_token_id: str | None


class UserUpdateIn(BaseModel):
    username: str
    password: str
    password_old: str


class UserUpdateOut(BaseModel):
    ...


class UserProtocol(Protocol[ID]):
    """User protocol that ORM model should follow."""

    id: ID
    email: str
    hashed_password: str
    is_active: bool
    is_superuser: bool
    is_verified: bool

    def __init__(self, *args, **kwargs) -> None:
        ...


UP = TypeVar("UP", bound=UserProtocol)


class UserRegistrationParamsOut(BaseModel):
    id: UUID
    username: str
    email: str
    first_name: str
    last_name: str


class LoginParamsIn(BaseModel):
    username: str
    password: str


class LoginParamsOut(TokenPair):
    ...


class LogoutParamsOut(BaseModel):
    ...


class RoleProtocol(Protocol[ID]):
    """Role protocol that ORM model should follow."""

    id: ID
    name: str

    def __init__(self, *args, **kwargs) -> None:
        ...


RP = TypeVar("RP", bound=RoleProtocol)


class RoleIn(BaseModel):
    name: str


class RoleOut(BaseModel):
    id: UUID
    name: str


class AccessRightProtocol(Protocol[ID]):
    """Access right protocol that ORM model should follow."""

    id: ID
    name: str
    roles: list[RP]

    def __init__(self, *args, **kwargs) -> None:
        ...


ARP = TypeVar("RP", bound=RoleProtocol)

class Message(BaseModel):
    text: str
    code: int


class SignInHistoryEvent(BaseModel):
    timestamp: datetime.datetime
    ip: str


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
