from typing import Iterable, Type
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status

from api.v1.common import ErrorCode
from authentication import Authenticator
from core import exceptions
from core.pagination import PaginateQueryParams
from db import models
from db.schemas import generics
from managers.rights import AccessRightManagerDependency, BaseAccessRightManager
from managers.role import BaseRoleManager, RoleManagerDependency
from managers.user import UserMgrDependencyType

RoleMgrDependencyType = RoleManagerDependency[
    models.RP, models.URP, generics.RC, generics.RU, models.URUP
]
RoleMgrType = BaseRoleManager[
    models.RP, models.URP, generics.RC, generics.RU, models.URUP
]
AccessRightMgrDependencyType = AccessRightManagerDependency[
    models.ARP, generics.ARC, generics.ARU, models.RARP, models.RARUP
]
AccessRightMgrType = BaseAccessRightManager[
    models.ARP, generics.ARC, generics.ARU, models.RARP, models.RARUP, models.ID
]


def get_access_rights_router(
    get_user_manager: UserMgrDependencyType,
    get_role_manager: RoleMgrDependencyType,
    get_access_right_manager: AccessRightMgrDependencyType,
    access_right_schema: Type[generics.AR],
    access_right_create_schema: Type[generics.ARC],
    access_right_update_schema: Type[generics.ARU],
    role_access_right_schema: Type[generics.RAR],
    role_access_right_update_schema: Type[generics.RARU],
    authenticator: Authenticator,
) -> APIRouter:
    router = APIRouter()
    router.prefix = "/api/v1"

    @router.get(
        "/rights/{access_right_id}",
        response_model=access_right_schema,
        summary="Get an access right",
        description="Get a item from the access right directory",
        response_description="Access Right entity",
        tags=['Access right'],
    )
    async def get_access_right(
        request: Request,
        access_right_id: UUID,
        access_right_manager: AccessRightMgrType = Depends(get_access_right_manager),
    ) -> access_right_schema:
        try:
            return await access_right_manager.get(access_right_id)

        except exceptions.AccessRightNotExists:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=ErrorCode.ACCESS_IS_NOT_EXISTS
            )

    @router.post(
        "/rights",
        response_model=access_right_schema,
        summary="Create a access right",
        description="Create a new item to the access rights directory",
        response_description="Access right entity",
        tags=['Access right'],
    )
    async def create_access(
        request: Request,
        access_right_create: access_right_create_schema,
        access_right_manager: AccessRightMgrType = Depends(get_access_right_manager),
    ) -> access_right_schema:
        try:
            access_right: access_right_schema = await access_right_manager.create(
                access_right_create, request=request
            )
            return access_right

        except exceptions.AccessRightAlreadyExists:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.UPDATE_ACCESS_NAME_ALREADY_EXISTS,
            )

    @router.get(
        "/rights/search",
        response_model=list[access_right_schema],
        summary="View all access rights",
        description="View all access rights",
        response_description="Access entities",
        tags=['Access right'],
    )
    async def search(
        request: Request,
        page_params: PaginateQueryParams = Depends(PaginateQueryParams),
        filter_param: str | None = None,
        access_right_manager: AccessRightMgrType = Depends(get_access_right_manager),
    ) -> Iterable[access_right_schema]:
        rights: Iterable[access_right_schema] = await access_right_manager.search(
            page_params, filter_param
        )
        return rights

    @router.put(
        "/rights",
        response_model=access_right_schema,
        summary="Change a access right",
        description="Change a access right",
        response_description="Changed access right entity",
        tags=['Access right'],
    )
    async def update_access_right(
        request: Request,
        access_right_update: access_right_update_schema,
        access_right_manager: AccessRightMgrType = Depends(get_access_right_manager),
    ) -> access_right_schema:
        try:
            access_right = await access_right_manager.get(access_right_update.id)

            access_right = await access_right_manager.update(
                access_right_update, access_right, request=request
            )
            return access_right

        except exceptions.AccessRightNotExists:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=ErrorCode.UPDATE_ACCESS_NAME_ALREADY_EXISTS,
            )

        except exceptions.RoleAlreadyExists:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.UPDATE_ROLE_NAME_ALREADY_EXISTS,
            )

    @router.delete(
        "/rights/{access_right_id}",
        response_model=access_right_schema,
        summary="Delete a access right",
        description="Delete a access right",
        response_description="Deleted access right entity",
        tags=['Access right'],
    )
    async def delete_access_right(
        request: Request,
        access_right_id: UUID,
        access_right_manager: AccessRightMgrType = Depends(get_access_right_manager),
    ) -> access_right_schema:
        try:
            access_right = await access_right_manager.get(access_right_id)

            access_right = await access_right_manager.delete(
                access_right, request=request
            )
            return access_right

        except exceptions.AccessRightNotExists:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=ErrorCode.ACCESS_IS_NOT_EXISTS
            )

    @router.get(
        "/roles/rights",
        responses={
            status.HTTP_204_NO_CONTENT: {"description": "Role has no access right."},
            status.HTTP_404_NOT_FOUND: {
                "description": "Role or access right not found."
            },
        },
        summary="Check roles access right",
        description="Check if role is assigned to the access right",
        response_description="Message entity",
        tags=['Access right'],
    )
    async def check_access_right(
        role_access_right: role_access_right_update_schema,
        access_right_manager: AccessRightMgrType = Depends(get_access_right_manager),
    ) -> None:
        try:
            if not await access_right_manager.check_role_acccess_right(
                role_access_right
            ):
                raise exceptions.UserHaveNotRole

        except exceptions.RoleHaveNotAccessRight:
            raise HTTPException(
                status.HTTP_204_NO_CONTENT, detail=ErrorCode.ROLE_IS_NOT_EXISTS
            )

    @router.post(
        "/roles/rights",
        status_code=status.HTTP_201_CREATED,
        summary="Assign a access right",
        description="Assign a access right to a role",
        response_description="Message entity",
        tags=['Access right'],
    )
    async def assign_access_right(
        role_access_right: role_access_right_update_schema,
        access_right_manager: AccessRightMgrType = Depends(get_access_right_manager),
        role_manager: RoleMgrType = Depends(get_role_manager),
    ) -> None:
        try:
            if not await role_manager.get(role_access_right.role_id):
                raise exceptions.RoleNotExists()

            if not await access_right_manager.get(role_access_right.access_right_id):
                raise exceptions.AccessRightNotExists()

            if await access_right_manager.check_role_acccess_right(role_access_right):
                raise exceptions.AccessRightAlreadyAssign()

            return await access_right_manager.assign_role_access_right(
                role_access_right
            )

        except exceptions.RoleNotExists:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=ErrorCode.ROLE_IS_NOT_EXISTS
            )
        except exceptions.AccessRightNotExists:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=ErrorCode.ACCESS_IS_NOT_EXISTS
            )

    @router.delete(
        "/roles/rights",
        status_code=status.HTTP_200_OK,
        responses={
            status.HTTP_204_NO_CONTENT: {
                "description": "Role or access right not found."
            }
        },
        summary="Unassign a access right",
        description="Unassign role's access right",
        response_description="Message entity",
        tags=['Access right'],
    )
    async def remove_role_access(
        role_access_right: role_access_right_update_schema,
        access_right_manager: AccessRightMgrType = Depends(get_access_right_manager),
        role_manager: RoleMgrType = Depends(get_role_manager),
    ) -> None:
        try:
            if not await role_manager.get(role_access_right.role_id):
                raise exceptions.RoleNotExists()

            if not await role_manager.get(role_access_right.access_right_id):
                raise exceptions.AccessRightNotExists()

            await access_right_manager.remove_role_access_right(role_access_right)

        except exceptions.RoleNotExists:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=ErrorCode.ROLE_IS_NOT_EXISTS
            )
        except exceptions.AccessRightNotExists:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=ErrorCode.ACCESS_IS_NOT_EXISTS
            )

    @router.get(
        "/roles/{roles_id}/rights",
        response_model=Iterable[models.ARP],
        summary="List the role's access right",
        description="Get list the role's access right",
        response_description="Message entity",
        tags=['Access right'],
    )
    async def get_role_rights(
        role_id: models.ID,
        access_right_manager: AccessRightMgrType = Depends(get_access_right_manager),
        role_manager: BaseAccessRightManager[
            models.ARP, generics.ARC, generics.ARU, models.RARP, models.RARUP, models.ID
        ] = Depends(get_role_manager),
    ) -> Iterable[models.ARP]:
        try:
            role = await role_manager.get(role_id)

            rights: Iterable[
                models.ARP
            ] = await access_right_manager.get_role_access_rights(role.id)
            return rights

        except exceptions.RoleNotExists:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=ErrorCode.ROLE_IS_NOT_EXISTS
            )

    return router
