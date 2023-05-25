import datetime
from typing import List, Optional, TypeVar, Generic
from uuid import UUID

from pydantic import BaseModel, EmailStr

import models as m

ID = TypeVar("ID", bound=UUID)


class CreateUpdateDictModel(BaseModel):
    def create_update_dict(self):
        return self.dict(
            exclude_unset=True,
            exclude={
                "id",
                "is_superuser",
                "is_active",
                "is_verified"
            },
        )

    def create_update_dict_superuser(self):
        return self.dict(exclude_unset=True, exclude={"id"})


class BaseUser(Generic[ID], CreateUpdateDictModel):
    """Base User model."""

    id: m.ID
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        orm_mode = True

    # TODO is self.from_orm method needed?


class BaseUserCreate(CreateUpdateDictModel):
    username: str
    password: str
    email: str
    first_name: str
    last_name: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class BaseUserUpdate(CreateUpdateDictModel):
    password: Optional[str]
    email: Optional[EmailStr]
    is_active: Optional[bool]
    is_superuser: Optional[bool]
    is_verified: Optional[bool]


U = TypeVar("U", bound=BaseUser)
UC = TypeVar("UC", bound=BaseUserCreate)
UU = TypeVar("UU", bound=BaseUserUpdate)


class BaseOAuthAccount(Generic[ID], BaseModel):
    id: ID
    oauth_name: str
    access_token: str
    expires_at: Optional[int] = None
    refresh_token: Optional[str] = None
    account_id: str
    account_email: str

    class Config:
        orm_mode = True


class SignInHistoryEvent(BaseModel):
    timestamp: datetime.datetime
    ip: str


class BaseRole(Generic[ID], CreateUpdateDictModel):
    """Base Role model."""

    id: m.ID
    name: str

    class Config:
        orm_mode = True


class BaseRoleCreate(CreateUpdateDictModel):
    name: str


class BaseRoleUpdate(CreateUpdateDictModel):
    id: m.ID
    name: str


R = TypeVar("R", bound=BaseRole)
RC = TypeVar("RC", bound=BaseRoleCreate)
RU = TypeVar("RU", bound=BaseRoleUpdate)