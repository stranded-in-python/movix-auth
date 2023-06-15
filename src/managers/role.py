from typing import Any, Generic, Iterable
from uuid import UUID

from fastapi import Depends, Request

from api import schemas
from core import exceptions
from core.dependency_types import DependencyCallable
from core.pagination import PaginateQueryParams
from db import getters, models_protocol
from db.base import BaseRoleDatabase, BaseUserRoleDatabase
from db.roles import SARoleDB, SAUserRoleDB
from db.schemas import models


class BaseRoleManager(
    Generic[models_protocol.UP, models_protocol.RP, models_protocol.URP]
):
    role_db: BaseRoleDatabase[models_protocol.RP, UUID]
    user_role_db: BaseUserRoleDatabase[models_protocol.URP, UUID]

    def __init__(
        self,
        role_db: BaseRoleDatabase[models_protocol.RP, UUID],
        user_role_db: BaseUserRoleDatabase[models_protocol.URP, UUID],
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
        self, role_create: schemas.BaseRoleCreate, request: Request | None = None
    ) -> models_protocol.RP:
        role = await self.role_db.get_by_name(role_create.name)
        if role:
            raise exceptions.RoleAlreadyExists

        role_dict = role_create.create_update_dict()

        created_role = await self.role_db.create(role_dict)

        await self.on_after_create(created_role, request)
        return created_role

    async def get(self, role_id: UUID) -> models_protocol.RP:
        role = await self.role_db.get_by_id(role_id)

        if role is None:
            raise exceptions.RoleNotExists()
        return role

    async def update(
        self,
        role_update: schemas.BaseRoleUpdate[UUID],
        role: models_protocol.RP,
        request: Request | None = None,
    ) -> models_protocol.RP:
        role_dict = role_update.create_update_dict()

        updated_role = await self.role_db.update(role, role_dict)

        await self.on_after_update(updated_role, request)
        return updated_role

    async def delete(
        self, role: models_protocol.RP, request: Request | None = None
    ) -> models_protocol.RP:
        await self.on_before_delete(role, request)

        await self.role_db.delete(role.id)

        await self.on_after_delete(role, request)

        return role

    async def search(
        self, pagination_params: PaginateQueryParams, filter_param: str | None = None
    ) -> Iterable[models_protocol.RP]:
        roles = await self.role_db.search(pagination_params, filter_param)

        return roles

    # endregion

    # region User roles registry

    async def check_user_role(
        self, user_role: models_protocol.UserRoleUpdateProtocol[UUID]
    ) -> bool:
        entry = await self.user_role_db.get_user_role(
            user_role.user_id, user_role.role_id
        )
        return True if entry else False

    async def assign_user_role(
        self, user_role: models_protocol.UserRoleUpdateProtocol[UUID]
    ) -> models_protocol.URP:
        entry = await self.user_role_db.assign_user_role(
            user_role.user_id, user_role.role_id
        )
        # entry_dict = user_role.create_update_dict()
        # entry = await self.user_role_db.assign_user_role(entry_dict)
        return entry

    async def remove_user_role(self, user_role_id: UUID):
        await self.user_role_db.remove_user_role(user_role_id)

    async def get_user_roles(self, user_id: UUID) -> Iterable[models_protocol.URP]:
        ids = await self.user_role_db.get_user_roles(user_id)

        return ids

    # endregion

    # region Handlers

    async def on_after_create(
        self, role: models_protocol.RP, request: Request | None = None
    ) -> None:
        ...

    async def on_after_update(
        self, role: models_protocol.RP, request: Request | None = None
    ) -> None:
        ...

    async def on_before_delete(
        self, role: models_protocol.RP, request: Request | None = None
    ) -> None:
        ...

    async def on_after_delete(
        self, role: models_protocol.RP, request: Request | None = None
    ) -> None:
        ...

    # endregion


RoleManagerDependency = DependencyCallable[
    BaseRoleManager[models_protocol.UP, models_protocol.RP, models_protocol.URP]
]


class RoleManager(
    models_protocol.UUIDIDMixin,
    BaseRoleManager[models.UserRead, models.RoleRead, models.UserRole],
):
    pass


async def get_role_manager(
    role_db: SARoleDB = Depends(getters.get_role_db),
    user_role_db: SAUserRoleDB = Depends(getters.get_user_role_db),
):
    yield RoleManager(role_db, user_role_db=user_role_db)
