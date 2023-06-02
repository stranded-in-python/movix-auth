import uuid

from pydantic import EmailStr

from db.schemas import generics


class UserRead(generics.ORMModeMixin, generics.BaseUser[uuid.UUID, EmailStr]):
    ...


class UserCreate(generics.ORMModeMixin, generics.BaseUserCreate[EmailStr]):
    ...


class UserUpdate(generics.ORMModeMixin, generics.BaseUserUpdate[EmailStr]):
    ...


class EventRead(
    generics.ORMModeMixin, generics.BaseSignInHistoryEvent[uuid.UUID, uuid.UUID]
):
    ...


class RoleRead(generics.ORMModeMixin, generics.BaseRole[uuid.UUID]):
    ...


class RoleUpdate(generics.ORMModeMixin, generics.BaseRoleUpdate[uuid.UUID]):
    ...


class RoleCreate(generics.ORMModeMixin, generics.BaseRoleCreate):
    ...


class UserRoleRead(
    generics.ORMModeMixin, generics.BaseUserRole[uuid.UUID, uuid.UUID, uuid.UUID]
):
    ...


class UserRoleUpdate(
    generics.ORMModeMixin, generics.BaseUserRoleUpdate[uuid.UUID, uuid.UUID]
):
    ...


class AccessRight(generics.ORMModeMixin, generics.BaseAccessRight[uuid.UUID]):
    ...


class AccessRightCreate(generics.ORMModeMixin, generics.BaseAccessRightCreate):
    ...


class AccessRightUpdate(
    generics.ORMModeMixin, generics.BaseAccessRightUpdate[uuid.UUID]
):
    ...


class RoleAccessRight(
    generics.ORMModeMixin, generics.BaseRoleAccessRight[uuid.UUID, uuid.UUID]
):
    ...


class Token(generics.ORMModeMixin, generics.BaseToken[uuid.UUID, uuid.UUID]):
    ...
