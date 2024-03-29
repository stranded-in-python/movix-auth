from datetime import datetime
from typing import Any, Iterable, Protocol, TypeVar
from uuid import UUID

import pydantic

import core.exceptions as ex
import db.schemas.models as models

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
    username: str | None
    email: EmailStr
    first_name: str | None
    last_name: str | None
    password: str
    is_active: bool | None
    is_superuser: bool | None


class UserProtocol(Protocol[ID, EmailStr]):
    """User protocol that ORM model should follow."""

    id: ID
    username: str | None
    email: EmailStr
    first_name: str | None
    last_name: str | None
    hashed_password: str
    is_active: bool
    is_verified: bool
    is_superuser: bool
    is_admin: bool


UP = TypeVar("UP", bound=UserProtocol[UUID, pydantic.EmailStr])
UC = TypeVar("UC", bound=UserCreateProtocol[str])


class ChannelProtocol(Protocol):
    """Channel protocol that ORM model should follow."""

    type: str
    value: str
    extra: dict | None


CHP = TypeVar("CHP", bound=ChannelProtocol)


class UserChannelProtocol(Protocol[ID]):
    """User/Channel protocol that ORM model should follow."""

    user_id: ID
    channels: Iterable[ChannelProtocol]


UCHP = TypeVar("UCHP", bound=UserChannelProtocol[UUID])


class OAuthAccountProtocol(Protocol[ID]):
    """OAuth account protocol that ORM model should follow."""

    id: ID
    oauth_name: str
    access_token: str
    expires_at: int | None
    refresh_token: str | None
    account_id: str
    account_email: str


OAP = TypeVar("OAP", bound=OAuthAccountProtocol[UUID])


class OAuthAccountsProtocol(Protocol[OAP]):
    oauth_accounts: list[OAP]


class UserOAuthProtocol(
    UserProtocol[ID, EmailStr], OAuthAccountsProtocol[OAP], Protocol
):
    """User protocol including a list of OAuth accounts."""

    ...


UOAP = TypeVar(
    "UOAP", bound=UserOAuthProtocol[UUID, pydantic.EmailStr, models.OAuthAccount]
)


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


class TokenProtocol(Protocol[ID]):
    """Access token protocol that ORM model should follow."""

    token: str
    user_id: ID
    created_at: datetime


TP = TypeVar("TP", bound=TokenProtocol[UUID])
