import uuid

import schemas as schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass


class RoleRead(schemas.BaseRole[uuid.UUID]):
    pass


class RoleUpdate(schemas.BaseRoleUpdate):
    pass


class RoleCreate(schemas.BaseRoleCreate):
    pass
