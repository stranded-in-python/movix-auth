import datetime
from typing import Generic, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, EmailStr

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
    is_active: bool = True
    is_superuser: bool = False

    class Config:
        orm_mode = True

    # TODO is self.from_orm method needed?


class BaseUserCreate(CreateUpdateUserDictModel):
    username: str
    password: str
    email: str
    first_name: str
    last_name: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False


class BaseUserUpdate(CreateUpdateUserDictModel):
    password: Optional[str]
    email: Optional[EmailStr]
    is_active: Optional[bool]
    is_superuser: Optional[bool]


U = TypeVar("U", bound=BaseUser)
UC = TypeVar("UC", bound=BaseUserCreate)
UU = TypeVar("UU", bound=BaseUserUpdate)


class BaseSignInHistoryEvent(CreateUpdateDictModel):
    timestamp: datetime.datetime | None
    fingerprint: str | None


SIHE = TypeVar("SIHE", bound=BaseSignInHistoryEvent)


class BaseRole(Generic[RoleID], CreateUpdateDictModel):
    """Base Role model."""

    id: RoleID
    name: str

    class Config:
        orm_mode = True


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

    class Config:
        orm_mode = True


class UserRoleUpdate(Generic[UserID, RoleID], CreateUpdateDictModel):
    user_id: UserID
    role_id: RoleID


UR = TypeVar("UR", bound=BaseUserRole)
URU = TypeVar("URU", bound=UserRoleUpdate)
