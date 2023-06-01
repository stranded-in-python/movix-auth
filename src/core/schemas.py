import uuid

from pydantic import BaseModel

from api import schemas


class UserRead(schemas.BaseUser):
    first_name: str
    last_name: str

    class Config:
        orm_mode = True


class UserCreate(schemas.BaseUserCreate):
    class Config:
        orm_mode = True


class UserUpdate(schemas.BaseUserUpdate):
    class Config:
        orm_mode = True


class EventRead(schemas.BaseSignInHistoryEvent):
    class Config:
        orm_mode = True


class RoleRead(schemas.BaseRole):
    class Config:
        orm_mode = True


class RoleUpdate(schemas.BaseRoleUpdate):
    class Config:
        orm_mode = True


class RoleCreate(schemas.BaseRoleCreate):
    class Config:
        orm_mode = True


class UserRoleRead(schemas.BaseUserRole):
    class Config:
        orm_mode = True


class UserRoleUpdate(schemas.UserRoleUpdate):
    class Config:
        orm_mode = True


class AccessRight(schemas.BaseAccessRight):
    class Config:
        orm_mode = True


class AccessRightCreate(schemas.BaseAccessRightCreate):
    class Config:
        orm_mode = True


class AccessRightUpdate(schemas.BaseAccessRightUpdate):
    class Config:
        orm_mode = True


class RoleAccessRight(schemas.BaseRoleAccessRight):
    class Config:
        orm_mode = True


class RoleAccessRightUpdate(schemas.BaseRoleAccessRightUpdate):
    class Config:
        orm_mode = True


class ID(BaseModel):
    id: uuid.UUID

    class Config:
        orm_mode = True
