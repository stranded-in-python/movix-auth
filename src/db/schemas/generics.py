import datetime
import enum
import uuid
from typing import Generic, Iterable, TypeVar

from pydantic import BaseModel, EmailStr

AccessRightID = TypeVar('AccessRightID', bound=uuid.UUID)
UserID = TypeVar("UserID", bound=uuid.UUID)
RoleID = TypeVar("RoleID", bound=uuid.UUID)
UserRoleID = TypeVar("UserRoleID", bound=uuid.UUID)
TokenID = TypeVar('TokenID', bound=uuid.UUID)
EventID = TypeVar('EventID', bound=uuid.UUID)
EmailString = TypeVar('EmailString', bound=EmailStr)
ID = TypeVar('ID', bound=uuid.UUID)


class ORMModeMixin:
    orm_mode = True


class CreateUpdateDictModel(BaseModel):
    def create_update_dict(self):
        return self.dict(exclude_unset=True, exclude={"id"})

    def create_update_dict_superuser(self):
        return self.dict(exclude_unset=True, exclude={"id"})


class CreateUpdateUserDictModel(CreateUpdateDictModel):
    def create_update_dict(self):
        return self.dict(
            exclude_unset=True, exclude={"id", "is_superuser", "is_admin", "is_active"}
        )


class BaseUser(Generic[UserID, EmailString], CreateUpdateUserDictModel):
    """Base User model."""

    id: UserID
    username: str | None
    email: EmailString
    hashed_password: str
    first_name: str | None
    last_name: str | None
    is_active: bool = True
    is_superuser: bool = False
    is_admin: bool = False
    is_verified: bool = False

    class Config(ORMModeMixin):
        ...


class BaseUserCreate(Generic[EmailString], CreateUpdateUserDictModel):
    username: str | None
    email: EmailString
    first_name: str | None
    last_name: str | None
    password: str
    is_active: bool = True
    is_superuser: bool = False
    is_admin: bool = False


class BaseUserUpdate(Generic[EmailString], CreateUpdateUserDictModel):
    password: str | None
    email: EmailStr | None
    first_name: str | None
    last_name: str | None
    is_active: bool = True
    is_superuser: bool = False
    is_admin: bool = False
    is_verified: bool = False


class ChannelEnum(enum.Enum):
    email = "email"


class BaseNotificationChannel(BaseModel):
    """Notification Channel model."""

    type: ChannelEnum
    value: str


class BaseUserChannels(Generic[UserID], BaseModel):
    user_id: UserID
    channels: Iterable[BaseNotificationChannel]

    class Config(ORMModeMixin):
        ...


class BaseSignInHistoryEvent(Generic[EventID, UserID], CreateUpdateDictModel):
    id: EventID
    user_id: UserID
    timestamp: datetime.datetime
    fingerprint: str


class BaseRole(Generic[RoleID], CreateUpdateDictModel):
    """Base Role model."""

    id: RoleID
    name: str


class BaseRoleCreate(CreateUpdateDictModel):
    name: str


class BaseRoleUpdate(Generic[RoleID], CreateUpdateDictModel):
    id: RoleID
    name: str


class BaseUserRole(Generic[UserRoleID, UserID, RoleID], CreateUpdateDictModel):
    id: UserRoleID
    user_id: UserID
    role_id: RoleID


class BaseUserRoleUpdate(Generic[UserID, RoleID], CreateUpdateDictModel):
    user_id: UserID
    role_id: RoleID


class BaseAccessRight(Generic[AccessRightID], CreateUpdateDictModel):
    id: AccessRightID
    name: str


class BaseAccessRightCreate(CreateUpdateDictModel):
    name: str


class BaseAccessRightUpdate(Generic[AccessRightID], CreateUpdateDictModel):
    id: AccessRightID
    name: str


class BaseRoleAccessRight(Generic[AccessRightID, RoleID], CreateUpdateDictModel):
    id: AccessRightID
    access_right_id: AccessRightID
    role_id: RoleID


class BaseRoleAccessRightUpdate(Generic[AccessRightID, RoleID], CreateUpdateDictModel):
    access_right_id: AccessRightID
    role_id: RoleID


class BaseToken(Generic[TokenID, UserID], BaseModel):
    id: TokenID
    token: str
    user_id: UserID
    created_at: datetime.datetime
