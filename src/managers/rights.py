import uuid
from typing import Generic, Iterable

from fastapi import Depends, Request

from core import exceptions
from core.dependency_types import DependencyCallable
from core.pagination import PaginateQueryParams
from db import access_rights, getters, models
from db.base import BaseAccessRightDatabase, BaseRoleAccessRightDatabase
from db.models import UUIDIDMixin
from db.schemas import generics, schemas
from managers.rights import BaseAccessRightManager


class BaseAccessRightManager(
    Generic[
        models.ARP, generics.ARC, generics.ARU, models.RARP, models.RARUP, models.ID
    ]
):
    access_rights_db: BaseAccessRightDatabase[models.ARP, models.ID]
    role_access_rights_db: BaseRoleAccessRightDatabase[models.RARP, models.ID]

    def __init__(
        self,
        access_rights_db: BaseAccessRightDatabase[models.ARP, models.ID],
        role_access_rights_db: BaseRoleAccessRightDatabase[models.RARP, models.ID],
    ):
        self.access_rights_db = access_rights_db
        self.role_access_rights_db = role_access_rights_db

    async def create(
        self, access_right_create: generics.ARC, request: Request | None = None
    ) -> models.ARP:
        access_right = await self.access_rights_db.get_by_name(access_right_create.name)
        if access_right:
            raise exceptions.AccessRightAlreadyExists

        accesses_dict = access_right_create.create_update_dict()

        created_access = await self.access_rights_db.create(accesses_dict)

        await self.on_after_create(created_access, request)
        return created_access

    async def get(self, access_right_id: models.ID) -> models.ARP:
        access_right = await self.access_rights_db.get(access_right_id)

        if access_right is None:
            raise exceptions.AccessRightNotExists()
        return access_right

    async def update(
        self,
        access_right_update: generics.ARU,
        access_right: models.ARP,
        request: Request | None = None,
    ) -> models.ARP:
        access_dict = access_right_update.create_update_dict()

        updated_access = await self.access_rights_db.update(access_right, access_dict)

        await self.on_after_update(updated_access, request)
        return updated_access

    async def delete(
        self, access_right: models.ARP, request: Request | None = None
    ) -> models.ARP:
        await self.on_before_delete(access_right, request)

        await self.access_rights_db.delete(access_right.id)

        await self.on_after_delete(access_right, request)

        return access_right

    async def search(
        self, pagination_params: PaginateQueryParams, filter_param: str | None = None
    ) -> Iterable[models.ARP]:
        access_right = await self.access_rights_db.search(
            pagination_params, filter_param
        )

        return access_right

    async def check_role_acccess_right(self, role_access_right: models.RARUP) -> bool:
        entry = await self.role_access_rights_db.get(
            role_access_right.role_id, role_access_right.access_right_id
        )
        return True if entry else False

    async def assign_role_access_right(
        self, role_access_right: models.RARUP
    ) -> models.RARP:
        entry = await self.role_access_rights_db.create(
            {
                'role_id': role_access_right.role_id,
                'access_right_id': role_access_right.access_right_id,
            }
        )
        return entry

    async def remove_role_access_right(self, role_access_right: models.RARUP):
        rar = await self.role_access_rights_db.get(
            role_access_right.role_id, role_access_right.access_right_id
        )
        if not rar:
            return None
        await self.role_access_rights_db.remove_role_access_right(rar)

    async def get_role_access_rights(self, role_id: models.ID) -> Iterable[models.RARP]:
        ids = await self.role_access_rights_db.get_role_access_rights(role_id)
        return ids

    async def on_after_create(
        self, access_right: models.ARP, request: Request | None = None
    ) -> None:
        ...

    async def on_after_update(
        self, access_right: models.ARP, request: Request | None = None
    ) -> None:
        ...

    async def on_before_delete(
        self, access_right: models.ARP, request: Request | None = None
    ) -> None:
        ...

    async def on_after_delete(
        self, access_right: models.ARP, request: Request | None = None
    ) -> None:
        ...


AccessRightManagerDependency = DependencyCallable[
    BaseAccessRightManager[
        models.ARP, generics.ARC, generics.ARU, models.RARP, models.RARUP, models.ID
    ]
]


class AccessRightManager(
    UUIDIDMixin,
    BaseAccessRightManager[
        schemas.AccessRight,
        schemas.AccessRightCreate,
        schemas.AccessRightUpdate,
        schemas.RoleAccessRight,
        schemas.RoleAccessRightUpdate,
        uuid.UUID,
    ],
):
    ...


async def get_access_right_manager(
    access_rights_db: access_rights.SAAccessRightDB = Depends(
        getters.get_access_rights_db
    ),
    role_access_rights_db: access_rights.SARoleAccessRightDB = Depends(
        getters.get_role_access_right_db
    ),
):
    yield AccessRightManager(access_rights_db, role_access_rights_db)
