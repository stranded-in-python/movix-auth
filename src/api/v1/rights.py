import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status

from api import schemas
from api.v1.common import ErrorCode
from authentication import Authenticator
from core import exceptions
from core.logger import logger
from core.pagination import PaginateQueryParams
from db import models_protocol
from managers.rights import AccessRightManagerDependency, BaseAccessRightManager
from managers.role import BaseRoleManager, RoleManagerDependency
from managers.user import BaseUserManager, UserManagerDependency
from rate_limiter import RateLimiter, RateLimitTime

logger()


def get_access_rights_router(
    get_user_manager: UserManagerDependency[
        models_protocol.UP,
        models_protocol.SIHE,
        models_protocol.OAP,
        models_protocol.UOAP,
    ],
    get_role_manager: RoleManagerDependency[
        models_protocol.UP, models_protocol.RP, models_protocol.URP
    ],
    get_access_right_manager: AccessRightManagerDependency[
        models_protocol.ARP, models_protocol.RARP
    ],
    access_right_schema: type[schemas.AR],
    access_right_create_schema: type[schemas.ARC],
    access_right_update_schema: type[schemas.ARU],
    role_access_right_schema: type[schemas.RAR],
    role_access_right_update_schema: type[schemas.RARU],
    authenticator: Authenticator[models_protocol.UP, models_protocol.SIHE],
) -> APIRouter:
    router = APIRouter()
    router.prefix = "/api/v1"

    get_current_adminuser = authenticator.current_user(active=True, admin=True)
    get_current_id = authenticator.current_user_uuid(active=True)

    @router.get(
        "/rights/search",
        response_model=list[access_right_schema],
        summary="View all access rights",
        description="View all access rights",
        response_description="Access entities",
        tags=['Access right'],
        dependencies=[
            Depends(RateLimiter(2, RateLimitTime(seconds=10), get_uuid=get_current_id))
        ],
    )
    async def search(  # pyright: ignore
        request: Request,
        page_params: PaginateQueryParams = Depends(PaginateQueryParams),
        filter_param: str | None = None,
        access_right_manager: BaseAccessRightManager[
            models_protocol.ARP, models_protocol.RARP
        ] = Depends(get_access_right_manager),
    ) -> list[access_right_schema]:
        rights = await access_right_manager.search(page_params, filter_param)
        logging.info("success")
        return list(access_right_schema.from_orm(right) for right in rights)

    @router.get(
        "/rights/{access_right_id}",
        response_model=access_right_schema,
        summary="Get an access right",
        description="Get a item from the access right directory",
        response_description="Access Right entity",
        tags=['Access right'],
    )
    async def get_access_right(  # pyright: ignore
        request: Request,
        access_right_id: UUID,
        access_right_manager: BaseAccessRightManager[
            models_protocol.ARP, models_protocol.RARP
        ] = Depends(get_access_right_manager),
    ) -> access_right_schema:
        try:
            access_right = await access_right_manager.get(access_right_id)
            logging.info("success:%s" % access_right.id)
            return access_right_schema.from_orm(access_right)

        except exceptions.AccessRightNotExists:
            logging.exception("AccessRightNotExists:%s" % access_right_id)
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=ErrorCode.ACCESS_IS_NOT_EXISTS
            )

    @router.post(
        "/rights",
        response_model=access_right_schema,
        summary="Create a access right",
        description="Create a new item to the access rights directory",
        response_description="Access right entity",
        dependencies=[
            Depends(get_current_adminuser),
            Depends(RateLimiter(2, RateLimitTime(seconds=10), get_uuid=get_current_id)),
        ],
        tags=['Access right'],
    )
    async def create_access(  # pyright: ignore
        request: Request,
        access_right_create: access_right_create_schema,
        access_right_manager: BaseAccessRightManager[
            models_protocol.ARP, models_protocol.RARP
        ] = Depends(get_access_right_manager),
    ) -> access_right_schema:
        try:
            access_right = await access_right_manager.create(
                access_right_create, request=request
            )
            logging.info("success:%s" % access_right.id)
            return access_right_schema.from_orm(access_right)

        except exceptions.AccessRightAlreadyExists:
            logging.exception("AccessRightAlreadyExists: %s" % access_right_create)
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.UPDATE_ACCESS_NAME_ALREADY_EXISTS,
            )

    @router.put(
        "/rights",
        response_model=access_right_schema,
        summary="Change a access right",
        description="Change a access right",
        response_description="Changed access right entity",
        dependencies=[
            Depends(get_current_adminuser),
            Depends(RateLimiter(2, RateLimitTime(seconds=10), get_uuid=get_current_id)),
        ],
        tags=['Access right'],
    )
    async def update_access_right(  # pyright: ignore
        request: Request,
        access_right_update: access_right_update_schema,
        access_right_manager: BaseAccessRightManager[
            models_protocol.ARP, models_protocol.RARP
        ] = Depends(get_access_right_manager),
    ) -> access_right_schema:
        try:
            access_right = await access_right_manager.get(access_right_update.id)

            access_right = await access_right_manager.update(
                access_right_update, access_right, request=request
            )
            logging.info("success:%s" % access_right.id)
            return access_right_schema.from_orm(access_right)

        except exceptions.AccessRightNotExists:
            logging.exception("AccessRightNotExists:%s" % access_right_update)
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=ErrorCode.UPDATE_ACCESS_NAME_ALREADY_EXISTS,
            )

        except exceptions.RoleAlreadyExists:
            logging.exception("RoleAlreadyExists:%s" % access_right_update)
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
        dependencies=[
            Depends(get_current_adminuser),
            Depends(RateLimiter(2, RateLimitTime(seconds=10), get_uuid=get_current_id)),
        ],
        tags=['Access right'],
    )
    async def delete_access_right(  # pyright: ignore
        request: Request,
        access_right_id: UUID,
        access_right_manager: BaseAccessRightManager[
            models_protocol.ARP, models_protocol.RARP
        ] = Depends(get_access_right_manager),
    ) -> access_right_schema:
        try:
            access_right = await access_right_manager.get(access_right_id)

            access_right = await access_right_manager.delete(
                access_right, request=request
            )
            logging.info("success:%s" % access_right.id)
            return access_right_schema.from_orm(access_right)

        except exceptions.AccessRightNotExists:
            logging.exception("AccessRightNotExists: %s" % access_right_id)
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
        dependencies=[
            Depends(RateLimiter(2, RateLimitTime(seconds=10), get_uuid=get_current_id))
        ],
    )
    async def check_access_right(  # pyright: ignore
        role_access_right: role_access_right_update_schema,
        access_right_manager: BaseAccessRightManager[
            models_protocol.ARP, models_protocol.RARP
        ] = Depends(get_access_right_manager),
    ) -> None:
        try:
            if not await access_right_manager.check_role_access_right(
                role_access_right
            ):
                raise exceptions.UserHasNoRole

            logging.info("success:%s" % role_access_right.access_right_id)

        except exceptions.RoleHaveNotAccessRight:
            logging.exception("RoleHaveNotAccessRight:%s" % role_access_right)
            raise HTTPException(
                status.HTTP_204_NO_CONTENT, detail=ErrorCode.ROLE_IS_NOT_EXISTS
            )

    @router.post(
        "/roles/rights",
        status_code=status.HTTP_201_CREATED,
        summary="Assign a access right",
        description="Assign a access right to a role",
        response_description="Message entity",
        dependencies=[
            Depends(get_current_adminuser),
            Depends(RateLimiter(2, RateLimitTime(seconds=10), get_uuid=get_current_id)),
        ],
        tags=['Access right'],
    )
    async def assign_access_right(  # pyright: ignore
        role_access_right: role_access_right_update_schema,
        access_right_manager: BaseAccessRightManager[
            models_protocol.ARP, models_protocol.RARP
        ] = Depends(get_access_right_manager),
        role_manager: BaseRoleManager[
            models_protocol.UP, models_protocol.RP, models_protocol.URP
        ] = Depends(get_role_manager),
    ) -> None:
        try:
            if not await role_manager.get(role_access_right.role_id):
                raise exceptions.RoleNotExists()

            if not await access_right_manager.get(role_access_right.access_right_id):
                raise exceptions.AccessRightNotExists()

            if await access_right_manager.check_role_access_right(role_access_right):
                raise exceptions.AccessRightAlreadyAssign()

            await access_right_manager.assign_role_access_right(role_access_right)

            logging.info("success:%s" % role_access_right.access_right_id)

        except exceptions.RoleNotExists:
            logging.exception("RoleNotExists:%s" % role_access_right)
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=ErrorCode.ROLE_IS_NOT_EXISTS
            )
        except exceptions.AccessRightNotExists:
            logging.exception("RoleNotExists:%s" % role_access_right)
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
        dependencies=[
            Depends(get_current_adminuser),
            Depends(RateLimiter(2, RateLimitTime(seconds=10), get_uuid=get_current_id)),
        ],
        tags=['Access right'],
    )
    async def remove_role_access(  # pyright: ignore
        role_access_right: role_access_right_update_schema,
        access_right_manager: BaseAccessRightManager[
            models_protocol.ARP, models_protocol.RARP
        ] = Depends(get_access_right_manager),
        role_manager: BaseRoleManager[
            models_protocol.UP, models_protocol.RP, models_protocol.URP
        ] = Depends(get_role_manager),
    ) -> None:
        try:
            if not await role_manager.get(role_access_right.role_id):
                raise exceptions.RoleNotExists()

            if not await role_manager.get(role_access_right.access_right_id):
                raise exceptions.AccessRightNotExists()

            await access_right_manager.remove_role_access_right(role_access_right)

            logging.info("success:%s" % role_access_right.access_right_id)

        except exceptions.RoleNotExists:
            logging.exception("RoleNotExists:%s" % role_access_right)
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=ErrorCode.ROLE_IS_NOT_EXISTS
            )
        except exceptions.AccessRightNotExists:
            logging.exception("AccessRightNotExists:%s" % role_access_right)
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=ErrorCode.ACCESS_IS_NOT_EXISTS
            )

    @router.get(
        "/roles/{roles_id}/rights",
        response_model=list[schemas.AR],
        summary="List the role's access right",
        description="Get list the role's access right",
        response_description="Message entity",
        tags=['Access right'],
        dependencies=[
            Depends(RateLimiter(2, RateLimitTime(seconds=10), get_uuid=get_current_id))
        ],
    )
    async def get_role_rights(  # pyright: ignore
        role_id: UUID,
        access_right_manager: BaseAccessRightManager[
            models_protocol.ARP, models_protocol.RARP
        ] = Depends(get_access_right_manager),
        role_manager: BaseRoleManager[
            models_protocol.UP, models_protocol.RP, models_protocol.URP
        ] = Depends(get_role_manager),
    ) -> list[schemas.AR]:
        try:
            role = await role_manager.get(role_id)

            rights = await access_right_manager.get_role_access_rights(role.id)

            logging.info("success:%s" % role_id)
            return list(access_right_schema.from_orm(right) for right in rights)

        except exceptions.RoleNotExists:
            logging.exception("RoleNotExists:%s" % role_id)
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=ErrorCode.ROLE_IS_NOT_EXISTS
            )

    @router.get(
        "/users/{user_id}/rights",
        response_model=list[schemas.AR],
        status_code=status.HTTP_200_OK,
        responses={
            status.HTTP_204_NO_CONTENT: {"description": "User have no rights."},
            status.HTTP_404_NOT_FOUND: {"description": "User or role not found."},
        },
        summary="List user rights",
        description="List all user's rights",
        tags=['Rights'],
        dependencies=[
            Depends(RateLimiter(2, RateLimitTime(seconds=10), get_uuid=get_current_id))
        ],
    )
    async def get_user_rights(  # pyright: ignore
        user_id: UUID,
        user_manager: BaseUserManager[
            models_protocol.UP,
            models_protocol.SIHE,
            models_protocol.OAP,
            models_protocol.UOAP,
        ] = Depends(get_user_manager),
        role_manager: BaseRoleManager[
            models_protocol.UP, models_protocol.RP, models_protocol.URP
        ] = Depends(get_role_manager),
        rights_manager: BaseAccessRightManager[
            models_protocol.ARP, models_protocol.RARP
        ] = Depends(get_access_right_manager),
    ) -> list[schemas.AR]:
        try:
            if not await user_manager.get(user_id):
                raise exceptions.UserNotExists

            roles = await role_manager.get_user_roles(user_id)
            if not roles:
                raise exceptions.UserHasNoRole

            roles_ids = [role.id for role in roles]

            rights = await rights_manager.get_roles_access_rights(roles_ids)
            if not rights:
                raise exceptions.UserHasNoRight

            logging.info(f"success:{user_id}")

            return list(schemas.AR.from_orm(right) for right in rights)

        except exceptions.UserNotExists:
            logging.exception(f"UserNotExists:{user_id}")
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=ErrorCode.USER_IS_NOT_EXISTS
            )
        except exceptions.UserHasNoRole:
            logging.exception(f"UserHasNoRole:{user_id}")
            raise HTTPException(
                status.HTTP_204_NO_CONTENT, detail=ErrorCode.USER_HAS_NO_ROLE
            )
        except exceptions.UserHasNoRight:
            logging.exception(f"UserHasNoRight:{user_id}")
            raise HTTPException(
                status.HTTP_204_NO_CONTENT, detail=ErrorCode.USER_HAS_NO_RIGHTS
            )

    return router
