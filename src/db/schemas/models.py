import uuid

from pydantic import EmailStr

from db.schemas import generics


class UserRead(generics.BaseUser[uuid.UUID, EmailStr]):
    hashed_password: str


class UserCreate(generics.BaseUserCreate[EmailStr]):
    password: str


class UserUpdate(generics.BaseUserUpdate[EmailStr]):
    ...


class EventRead(generics.BaseSignInHistoryEvent[uuid.UUID, uuid.UUID]):
    class Config(generics.ORMModeMixin):
        ...


class RoleRead(generics.BaseRole[uuid.UUID]):
    class Config(generics.ORMModeMixin):
        ...


class RoleUpdate(generics.BaseRoleUpdate[uuid.UUID]):
    class Config(generics.ORMModeMixin):
        ...

class RoleCreate(generics.BaseRoleCreate):
    class Config(generics.ORMModeMixin):
        ...


class UserRoleRead(generics.BaseUserRole[uuid.UUID, uuid.UUID, uuid.UUID]):
    class Config(generics.ORMModeMixin):
        ...


class UserRoleUpdate(generics.BaseUserRoleUpdate[uuid.UUID, uuid.UUID]):
    class Config(generics.ORMModeMixin):
        ...


class AccessRight(generics.BaseAccessRight[uuid.UUID]):
    class Config(generics.ORMModeMixin):
        ...


class AccessRightCreate(generics.BaseAccessRightCreate):
    class Config(generics.ORMModeMixin):
        ...


class AccessRightUpdate(generics.BaseAccessRightUpdate[uuid.UUID]):
    class Config(generics.ORMModeMixin):
        ...


class RoleAccessRight(generics.BaseRoleAccessRight[uuid.UUID, uuid.UUID]):
    class Config(generics.ORMModeMixin):
        ...


class RoleAccessRightUpdate(generics.BaseRoleAccessRightUpdate[uuid.UUID, uuid.UUID]):
    class Config(generics.ORMModeMixin):
        ...


class Token(generics.BaseToken[uuid.UUID, uuid.UUID]):
    class Config(generics.ORMModeMixin):
        ...
