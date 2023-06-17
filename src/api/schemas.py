import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, EmailStr

AccessRightID = TypeVar('AccessRightID', bound=UUID)
UserID = TypeVar("UserID", bound=UUID)
RoleID = TypeVar("RoleID", bound=UUID)
UserRoleID = TypeVar("UserRoleID", bound=UUID)


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


class BaseUser(Generic[UserID], CreateUpdateUserDictModel):
    """Base User model."""

    id: UserID
    username: str
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False
    is_admin: bool = False


class BaseUserCreate(CreateUpdateUserDictModel):
    password: str
    email: str
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = True
    is_superuser: bool | None = False
    is_admin: bool = False


class BaseUserUpdate(CreateUpdateUserDictModel):
    password: str | None = None
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    is_admin: bool = False


class UserRead(BaseUser[UUID]):
    class Config:
        orm_mode = True


class UserCreate(BaseUserCreate):
    class Config:
        orm_mode = True


class UserUpdate(BaseUserUpdate):
    class Config:
        orm_mode = True


U = TypeVar("U", bound=UserRead)
UC = TypeVar("UC", bound=UserCreate)
UU = TypeVar("UU", bound=UserUpdate)


class BaseOAuthAccount(Generic[UserID], BaseModel):
    """Base OAuth account model."""

    id: UserID
    oauth_name: str
    access_token: str
    expires_at: int | None = None
    refresh_token: str | None = None
    account_id: str
    account_email: str

    class Config:
        orm_mode = True


class BaseOAuthAccountMixin(BaseModel):
    """Adds OAuth accounts list to a User model."""

    oauth_accounts: list[BaseOAuthAccount] = []


class BaseSignInHistoryEvent(CreateUpdateDictModel):
    timestamp: datetime.datetime | None
    fingerprint: str | None


SIHE = TypeVar("SIHE", bound=BaseSignInHistoryEvent)


class EventRead(BaseSignInHistoryEvent):
    class Config:
        orm_mode = True


class BaseRole(Generic[RoleID], CreateUpdateDictModel):
    """Base Role model."""

    id: RoleID
    name: str


class BaseRoleCreate(CreateUpdateDictModel):
    name: str


class BaseRoleUpdate(Generic[RoleID], CreateUpdateDictModel):
    id: RoleID
    name: str


class RoleRead(BaseRole[UUID]):
    class Config:
        orm_mode = True


class RoleCreate(BaseRoleCreate):
    class Config:
        orm_mode = True


class RoleUpdate(BaseRoleUpdate[UUID]):
    class Config:
        orm_mode = True


R = TypeVar("R", bound=RoleRead)
RC = TypeVar("RC", bound=RoleCreate)
RU = TypeVar("RU", bound=RoleUpdate)


class BaseUserRole(Generic[UserRoleID, UserID, RoleID], CreateUpdateDictModel):
    id: UserRoleID
    user_id: UserID
    role_id: RoleID


class BaseUserRoleUpdate(Generic[UserID, RoleID], CreateUpdateDictModel):
    user_id: UserID
    role_id: RoleID


class UserRoleRead(BaseUserRole[UUID, UUID, UUID]):
    class Config:
        orm_mode = True


class UserRoleUpdate(BaseUserRoleUpdate[UUID, UUID]):
    class Config:
        orm_mode = True


UR = TypeVar("UR", bound=UserRoleRead)
URU = TypeVar("URU", bound=UserRoleUpdate)


class BaseAccessRight(Generic[AccessRightID], CreateUpdateDictModel):
    id: AccessRightID
    name: str


class BaseAccessRightCreate(CreateUpdateDictModel):
    name: str


class BaseAccessRightUpdate(Generic[AccessRightID], CreateUpdateDictModel):
    id: AccessRightID
    name: str


class AccessRightRead(BaseAccessRight[UUID]):
    class Config:
        orm_mode = True


class AccessRightCreate(BaseAccessRightCreate):
    class Config:
        orm_mode = True


class AccessRightUpdate(BaseAccessRightUpdate[UUID]):
    class Config:
        orm_mode = True


AR = TypeVar("AR", bound=AccessRightRead)
ARC = TypeVar("ARC", bound=AccessRightCreate)
ARU = TypeVar("ARU", bound=AccessRightUpdate)


class BaseRoleAccessRight(Generic[AccessRightID, RoleID], CreateUpdateDictModel):
    id: AccessRightID
    access_right_id: AccessRightID
    role_id: RoleID


class BaseRoleAccessRightUpdate(Generic[AccessRightID, RoleID], CreateUpdateDictModel):
    access_right_id: AccessRightID
    role_id: RoleID


class RoleAccessRightRead(BaseRoleAccessRight[UUID, UUID]):
    class Config:
        orm_mode = True


class RoleAccessRightUpdate(BaseRoleAccessRightUpdate[UUID, UUID]):
    class Config:
        orm_mode = True


RAR = TypeVar("RAR", bound=BaseRoleAccessRight[UUID, UUID])
RARU = TypeVar("RARU", bound=BaseRoleAccessRightUpdate[UUID, UUID])
