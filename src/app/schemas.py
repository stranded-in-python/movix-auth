import uuid

from pydantic import BaseModel

import schemas as schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    first_name: str
    last_name: str


class UserCreate(schemas.BaseUserCreate):
    class Config:
        orm_mode = True


class UserUpdate(schemas.BaseUserUpdate):
    class Config:
        orm_mode = True


class EventRead(schemas.BaseSignInHistoryEvent):
    class Config:
        orm_mode = True


class RoleRead(schemas.BaseRole[uuid.UUID]):
    class Config:
        orm_mode = True


class RoleUpdate(schemas.BaseRoleUpdate):
    pass


class RoleCreate(schemas.BaseRoleCreate):
    pass


class UserRoleRead(schemas.BaseUserRole):
    pass


class UserRoleUpdate(schemas.UserRoleUpdate):
    pass


class ID(BaseModel):
    id: uuid.UUID

    class Config:
        orm_mode = True