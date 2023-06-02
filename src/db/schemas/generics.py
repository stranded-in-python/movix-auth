import datetime
import uuid
from typing import Generic, TypeVar

from pydantic import BaseModel, EmailStr

AccessRightID = TypeVar('AccessRightID', bound=uuid.UUID)
UserID = TypeVar("UserID", bound=uuid.UUID)
RoleID = TypeVar("RoleID", bound=uuid.UUID)
UserRoleID = TypeVar("UserRoleID", bound=uuid.UUID)
TokenID = TypeVar('TokenID', bound=uuid.UUID)
EventID = TypeVar('EventID', bound=uuid.UUID)
EmailString = TypeVar('EmailString', bound=EmailStr)


class CreateUpdateDictModel(BaseModel):
    def create_update_dict(self):
        return self.dict(exclude_unset=True, exclude={"id"})

    def create_update_dict_superuser(self):
        return self.dict(exclude_unset=True, exclude={"id"})


class CreateUpdateUserDictModel(CreateUpdateDictModel):
    def create_update_dict(self):
        return self.dict(
            exclude_unset=True, exclude={"id", "is_superuser", "is_active"}
        )


class BaseUser(Generic[UserID, EmailString], CreateUpdateUserDictModel):
    """Base User model."""

    id: UserID
    username: str
    email: EmailString
    first_name: str
    last_name: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False


class BaseUserCreate(Generic[EmailString], CreateUpdateUserDictModel):
    username: str
    email: EmailString
    first_name: str
    last_name: str
    password: str
    is_active: bool = True
    is_superuser: bool = False


class BaseUserUpdate(Generic[EmailString], CreateUpdateUserDictModel):
    password: str | None
    email: EmailStr | None
    first_name: str
    last_name: str
    is_active: bool = True
    is_superuser: bool = False


U = TypeVar("U", bound=BaseUser)
UC = TypeVar("UC", bound=BaseUserCreate)
UU = TypeVar("UU", bound=BaseUserUpdate)


class BaseSignInHistoryEvent(Generic[EventID, UserID], CreateUpdateDictModel):
    id: EventID
    user_id: UserID
    timestamp: datetime.datetime
    fingerprint: str


SIHE = TypeVar("SIHE", bound=BaseSignInHistoryEvent)


class BaseRole(Generic[RoleID], CreateUpdateDictModel):
    """Base Role model."""

    id: RoleID
    name: str


class BaseRoleCreate(CreateUpdateDictModel):
    name: str


class BaseRoleUpdate(Generic[RoleID], CreateUpdateDictModel):
    id: RoleID
    name: str


R = TypeVar("R", bound=BaseRole)
RC = TypeVar("RC", bound=BaseRoleCreate)
RU = TypeVar("RU", bound=BaseRoleUpdate)


class BaseUserRole(Generic[UserRoleID, UserID, RoleID], CreateUpdateDictModel):
    id: UserRoleID
    user_id: UserID
    role_id: RoleID


class BaseUserRoleUpdate(Generic[UserID, RoleID], CreateUpdateDictModel):
    user_id: UserID
    role_id: RoleID


UR = TypeVar("UR", bound=BaseUserRole)
URU = TypeVar("URU", bound=BaseUserRoleUpdate)


class BaseAccessRight(Generic[AccessRightID], CreateUpdateDictModel):
    id: AccessRightID
    name: str


class BaseAccessRightCreate(CreateUpdateDictModel):
    name: str


class BaseAccessRightUpdate(Generic[AccessRightID], CreateUpdateDictModel):
    id: AccessRightID
    name: str


AR = TypeVar("AR", bound=BaseAccessRight)
ARC = TypeVar("ARC", bound=BaseAccessRightCreate)
ARU = TypeVar("ARU", bound=BaseAccessRightUpdate)


class BaseRoleAccessRight(Generic[AccessRightID, RoleID], CreateUpdateDictModel):
    id: AccessRightID
    access_right_id: AccessRightID
    role_id: RoleID


class BaseRoleAccessRightUpdate(Generic[AccessRightID, RoleID], CreateUpdateDictModel):
    access_right_id: AccessRightID
    role_id: RoleID


RAR = TypeVar("RAR", bound=BaseRoleAccessRight)
RARU = TypeVar("RARU", bound=BaseRoleAccessRightUpdate)


class ORMModeMixin:
    class Config:
        orm_mode = True


class BaseToken(Generic[TokenID, UserID], BaseModel):
    id: TokenID
    token: str
    user_id: UserID
    created_at: datetime.datetime


AT = TypeVar('AT', bound=BaseToken)
