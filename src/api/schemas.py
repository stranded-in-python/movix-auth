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
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool = True
    is_superuser: bool = False


class BaseUserCreate(CreateUpdateUserDictModel):
    username: str
    password: str
    email: str
    first_name: str
    last_name: str
    is_active: bool | None = True
    is_superuser: bool | None = False


class BaseUserUpdate(CreateUpdateUserDictModel):
    password: str | None
    email: EmailStr | None
    first_name: str | None
    last_name: str | None
    is_active: bool | None
    is_superuser: bool | None


U = TypeVar("U", bound=BaseUser)
UC = TypeVar("UC", bound=BaseUserCreate)
UU = TypeVar("UU", bound=BaseUserUpdate)


class UserRead(BaseUser[UUID]):
    class Config:
        orm_mode = True


class UserCreate(BaseUserCreate):
    class Config:
        orm_mode = True


class UserUpdate(BaseUserUpdate):
    class Config:
        orm_mode = True


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


R = TypeVar("R", bound=BaseRole)
RC = TypeVar("RC", bound=BaseRoleCreate)
RU = TypeVar("RU", bound=BaseRoleUpdate)


class BaseUserRole(Generic[UserRoleID, UserID, RoleID], CreateUpdateDictModel):
    id: UserRoleID
    user_id: UserID
    role_id: RoleID


class UserRoleUpdate(Generic[UserID, RoleID], CreateUpdateDictModel):
    user_id: UserID
    role_id: RoleID


UR = TypeVar("UR", bound=BaseUserRole)
URU = TypeVar("URU", bound=UserRoleUpdate)


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
