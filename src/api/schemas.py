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
