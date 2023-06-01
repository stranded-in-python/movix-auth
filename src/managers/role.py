from typing import Any, Generic
from uuid import UUID

from fastapi import Depends, Request

from api import schemas
from api.roles import APIRoles
from app.services.users import auth_backend, get_user_manager
from core import exceptions
from core.dependency_types import DependencyCallable
from core.pagination import PaginateQueryParams
from db import base, db, models, roles
from db.base import BaseRoleDatabase, BaseUserRoleDatabase
from db.models import UUIDIDMixin
from db.roles import SARoleDB, SAUserRoleDB
from managers.role import BaseRoleManager


class BaseRoleManager(Generic[models.RP, models.URP, models.URUP]):
    role_db: BaseRoleDatabase[models.RP, UUID]
    user_role_db: BaseUserRoleDatabase[models.URP, models.URUP, UUID]

    def __init__(
        self,
        role_db: BaseRoleDatabase[models.RP, UUID],
        user_role_db: BaseUserRoleDatabase[models.URP, models.URUP, UUID],
    ):
        self.role_db = role_db
        self.user_role_db = user_role_db

    # region Utile
    def parse_id(self, value: Any) -> UUID:
        """
        Parse a value into a correct UUID instance.
        Must implement in Generic[UUID]

        :param value: The value to parse.
        :raises InvalidID: The UUID value is invalid.
        :return: An UUID object.
        """
        raise NotImplementedError()

    # endregion

    # region User dictionary

    async def create(
        self, role_create: schemas.RC, request: Request | None = None
    ) -> models.RP:
        role = await self.role_db.get_by_name(role_create.name)
        if role:
            raise exceptions.RoleAlreadyExists

        role_dict = role_create.create_update_dict()

        created_role = await self.role_db.create(role_dict)

        await self.on_after_create(created_role, request)
        return created_role

    async def get(self, role_id: UUID) -> models.RP:
        role = await self.role_db.get_by_id(role_id)

        if role is None:
            raise exceptions.RoleNotExists()
        return role

    async def update(
        self, role_update: schemas.RU, role: models.RP, request: Request | None = None
    ) -> models.RP:
        role_dict = role_update.create_update_dict()

        updated_role = await self.role_db.update(role, role_dict)

        await self.on_after_update(updated_role, request)
        return updated_role

    async def delete(
        self, role: models.RP, request: Request | None = None
    ) -> models.RP:
        await self.on_before_delete(role, request)

        await self.role_db.delete(role.id)

        await self.on_after_delete(role, request)

        return role

    async def search(
        self, pagination_params: PaginateQueryParams, filter_param: str | None = None
    ) -> list[models.RP]:
        roles = await self.role_db.search(pagination_params, filter_param)

        return roles

    # endregion

    # region User roles registry

    async def check_user_role(self, user_role: models.URUP) -> bool:
        entry = await self.user_role_db.get_user_role(
            user_role.user_id, user_role.role_id
        )
        return True if entry else False

    async def assign_user_role(self, user_role: models.URUP):
        entry = await self.user_role_db.assign_user_role(
            user_role.user_id, user_role.role_id
        )
        # entry_dict = user_role.create_update_dict()
        # entry = await self.user_role_db.assign_user_role(entry_dict)
        return entry

    async def remove_user_role(self, user_role: models.URUP):
        await self.user_role_db.remove_user_role(user_role)

    async def get_user_roles(self, user_id):
        ids = await self.user_role_db.get_user_roles(user_id)

        return ids

    # endregion

    # region Handlers

    async def on_after_create(
        self, role: models.RP, request: Request | None = None
    ) -> None:
        ...

    async def on_after_update(
        self, role: models.RP, request: Request | None = None
    ) -> None:
        ...

    async def on_before_delete(
        self, role: models.RP, request: Request | None = None
    ) -> None:
        ...

    async def on_after_delete(
        self, role: models.RP, request: Request | None = None
    ) -> None:
        ...

    # endregion


RoleManagerDependency = DependencyCallable[
    BaseRoleManager[models.RP, models.URP, models.URUP]
]


class RoleManager(UUIDIDMixin, BaseRoleManager[SARole, UUID]):
    pass


async def get_role_manager(
    role_db: SARoleDB = Depends(get_role_db),
    user_role_db: SAUserRoleDB = Depends(get_user_role_db),
):
    yield RoleManager(role_db, user_role_db=user_role_db)


api_roles = APIRoles[User, UUID](get_user_manager, get_role_manager, [auth_backend])
