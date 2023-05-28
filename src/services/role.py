from typing import Generic, Any, Optional, TypeVar

from fastapi import Request, Response

import models
import schemas
from core import exceptions
from core.dependency_types import DependencyCallable
from db.base import BaseRoleDatabase


class BaseRoleManager(
    Generic[models.RP, models.ID]
):
    role_db: BaseRoleDatabase[models.RP, models.ID]

    def __init__(
        self,
        role_db: BaseRoleDatabase[models.RP, models.ID]
    ):
        self.role_db = role_db

    def parse_id(self, value: Any) -> models.ID:
        """
        Parse a value into a correct models.ID instance.
        Must implement in Generic[models.ID]

        :param value: The value to parse.
        :raises InvalidID: The models.ID value is invalid.
        :return: An models.ID object.
        """
        raise NotImplementedError()

    async def create(
            self,
            role_create: schemas.RC,
            request: Request | None = None
    ) -> models.RP:

        role_dict = role_create.create_update_dict()

        created_role = await self.role_db.create(role_dict)

        await self.on_after_create(created_role, request)
        return created_role

    async def get(self, role_id: models.ID) -> models.RP:
        role = await self.role_db.get(role_id)

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
    ) -> None:

        await self.on_before_delete(role, request)

        await self.role_db.delete(role.id)

        await self.on_after_delete(role, request)

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


RoleManagerDependency = DependencyCallable[BaseRoleManager[models.RP, models.ID]]
