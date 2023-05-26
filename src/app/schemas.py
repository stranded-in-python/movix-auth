import uuid

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
