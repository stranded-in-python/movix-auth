from typing import Generic, Any, Optional, TypeVar

from fastapi import Request, Response

import models
import schemas
from core import exceptions
from core.dependency_types import DependencyCallable
from core.pagination import PaginateQueryParams
from db.base import BaseRoleDatabase, BaseUserRoleDatabase


class BaseRoleManager(
    Generic[models.RP, models.ID]
):
    role_db: BaseRoleDatabase[models.RP, models.ID]
    user_role_db: BaseUserRoleDatabase[models.URP, models.ID]

    def __init__(
            self,
            role_db: BaseRoleDatabase[models.RP, models.ID],
            user_role_db: BaseUserRoleDatabase[models.URP, models.ID]
    ):
        self.role_db = role_db
        self.user_role_db = user_role_db

    # region Utile
    def parse_id(self, value: Any) -> models.ID:
        """
        Parse a value into a correct models.ID instance.
        Must implement in Generic[models.ID]

        :param value: The value to parse.
        :raises InvalidID: The models.ID value is invalid.
        :return: An models.ID object.
        """
        raise NotImplementedError()

    # endregion

    # region User dictionary

    async def create(
            self,
            role_create: schemas.RC,
            request: Request | None = None
    ) -> models.RP:
        role = await self.role_db.get_by_name(role_create.name)
        if role:
            raise exceptions.RoleAlreadyExists

        role_dict = role_create.create_update_dict()

        created_role = await self.role_db.create(role_dict)

        await self.on_after_create(created_role, request)
        return created_role

    async def get(self, role_id: models.ID) -> models.RP:
        role = await self.role_db.get_by_id(role_id)

        if role is None:
            raise exceptions.RoleNotExists()
        return role

    async def update(
            self,
            role_update: schemas.RU,
            role: models.RP,
            request: Optional[Request] = None,
    ) -> models.UP:
        role_dict = role_update.create_update_dict()

        updated_user = await self.role_db.update(role, role_dict)

        await self.on_after_update(updated_user, request)
        return updated_user

    async def delete(
            self,
            role: models.RP,
            request: Optional[Request] = None,
    ) -> models.RP:
        await self.on_before_delete(role, request)

        await self.role_db.delete(role.id)

        await self.on_after_delete(role, request)

        return role

    async def search(
            self,
            pagination_params: PaginateQueryParams,
            filter_param: str | None = None,
    ) -> list[models.RP]:
        roles = await self.role_db.search(pagination_params, filter_param)

        return roles

    # endregion

    # region User roles registry

    async def check_user_role(
            self,
            user_role: schemas.URU,
    ) -> bool:
        entry = await self.user_role_db.get_user_role(
            user_role.user_id,
            user_role.role_id
        )
        return True if entry else False

    async def assign_user_role(
            self,
            user_role: schemas.URU,
    ):
        entry_dict = user_role.create_update_dict()
        entry = await self.user_role_db.assign_user_role(
            entry_dict
        )
        return entry

    async def remove_user_role(
            self,
            user_role: schemas.URU
    ):
        await self.user_role_db.remove_user_role(user_role)

    async def get_user_roles(self, user_id):
        ids = await self.user_role_db.get_user_roles(user_id)

        return ids

    # endregion

    # region Handlers

    async def on_after_create(
            self, user: models.UP, request: Optional[Request] = None
    ) -> None:
        ...

    async def on_after_update(
            self,
            user: models.UP,
            request: Optional[Request] = None,
    ) -> None:
        ...

    async def on_before_delete(
            self, user: models.UP, request: Optional[Request] = None
    ) -> None:
        ...

    async def on_after_delete(
            self, user: models.UP, request: Optional[Request] = None
    ) -> None:
        ...

    # endregion


RoleManagerDependency = DependencyCallable[BaseRoleManager[models.RP, models.ID]]
