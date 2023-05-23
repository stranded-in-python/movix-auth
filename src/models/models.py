from uuid import UUID

from pydantic import BaseModel


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


class UserRegistrationParamsIn(BaseModel):
    username: str
    password: str
    email: str
    first_name: str
    last_name: str


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
