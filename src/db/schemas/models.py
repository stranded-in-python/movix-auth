import uuid
from typing import TypeVar

from pydantic import EmailStr

from db.schemas import generics


class UserRead(generics.BaseUser[uuid.UUID, EmailStr]):
    hashed_password: str


class UserCreate(generics.BaseUserCreate[EmailStr]):
    password: str


class UserUpdate(generics.BaseUserUpdate[EmailStr]):
    ...


U = TypeVar("U", bound=UserRead)
UC = TypeVar("UC", bound=UserCreate)
UU = TypeVar("UU", bound=UserUpdate)


class EventRead(generics.BaseSignInHistoryEvent[uuid.UUID, uuid.UUID]):
    class Config(generics.ORMModeMixin):
        ...


SIHE = TypeVar("SIHE", bound=EventRead)


class RoleRead(generics.BaseRole[uuid.UUID]):
    class Config(generics.ORMModeMixin):
        ...


class RoleUpdate(generics.BaseRoleUpdate[uuid.UUID]):
    class Config(generics.ORMModeMixin):
        ...


class RoleCreate(generics.BaseRoleCreate):
    class Config(generics.ORMModeMixin):
        ...


R = TypeVar("R", bound=RoleRead)
RC = TypeVar("RC", bound=RoleUpdate)
RU = TypeVar("RU", bound=RoleCreate)


class UserRole(generics.BaseUserRole[uuid.UUID, uuid.UUID, uuid.UUID]):
    class Config(generics.ORMModeMixin):
        ...


class UserRoleUpdate(generics.BaseUserRoleUpdate[uuid.UUID, uuid.UUID]):
    class Config(generics.ORMModeMixin):
        ...


UR = TypeVar("UR", bound=UserRole)
URU = TypeVar("URU", bound=UserRoleUpdate)


class AccessRight(generics.BaseAccessRight[uuid.UUID]):
    class Config(generics.ORMModeMixin):
        ...


class AccessRightCreate(generics.BaseAccessRightCreate):
    class Config(generics.ORMModeMixin):
        ...


class AccessRightUpdate(generics.BaseAccessRightUpdate[uuid.UUID]):
    class Config(generics.ORMModeMixin):
        ...


AR = TypeVar("AR", bound=AccessRight)
ARC = TypeVar("ARC", bound=AccessRightCreate)
ARU = TypeVar("ARU", bound=AccessRightUpdate)


class RoleAccessRight(generics.BaseRoleAccessRight[uuid.UUID, uuid.UUID]):
    class Config(generics.ORMModeMixin):
        ...


class RoleAccessRightUpdate(generics.BaseRoleAccessRightUpdate[uuid.UUID, uuid.UUID]):
    class Config(generics.ORMModeMixin):
        ...


RAR = TypeVar("RAR", bound=RoleAccessRight)
RARU = TypeVar("RARU", bound=RoleAccessRightUpdate)


class Token(generics.BaseToken[uuid.UUID, uuid.UUID]):
    class Config(generics.ORMModeMixin):
        ...


AT = TypeVar('AT', bound=Token)
