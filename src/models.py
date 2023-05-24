from typing import Protocol, TypeVar
from uuid import UUID

from pydantic import BaseModel

ID = TypeVar("ID", bound=UUID)


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


class RoleIn(BaseModel):
    name: str


class RoleOut(BaseModel):
    id: UUID
    name: str


class Message(BaseModel):
    text: str
    code: int
