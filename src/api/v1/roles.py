from typing import Type
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status

from api import schemas
from api.v1.common import ErrorCode
from authentication import Authenticator
from core import exceptions
from core.pagination import PaginateQueryParams
from db import models_protocol
from managers.role import BaseRoleManager, RoleManagerDependency
from managers.user import BaseUserManager, UserManagerDependency

import logging
from core.logger import logger

logger()

def get_roles_router(
    get_user_manager: UserManagerDependency[models_protocol.UP, models_protocol.SIHE],
    get_role_manager: RoleManagerDependency[
        models_protocol.UP, models_protocol.RP, models_protocol.URP
    ],
    role_schema: Type[schemas.R],
    role_create_schema: Type[schemas.RC],
    role_update_schema: Type[schemas.RU],
    user_role_schema: Type[schemas.UR],
    user_role_update_schema: Type[schemas.URU],
    authenticator: Authenticator[models_protocol.UP, models_protocol.SIHE],
) -> APIRouter:
    router = APIRouter()
    router.prefix = "/api/v1"

    get_current_adminuser = authenticator.current_user(active=True, admin=True)

    @router.get(
        "/roles/search",
        response_model=list[role_schema],
        summary="View all roles",
        description="View all roles",
        response_description="Role entities",
        dependencies=[Depends(get_current_adminuser)],
        tags=['Roles'],
    )
    async def search(  # pyright: ignore
        request: Request,
        page_params: PaginateQueryParams = Depends(PaginateQueryParams),
        filter_param: str | None = None,
        role_manager: BaseRoleManager[
            models_protocol.UP, models_protocol.RP, models_protocol.URP
        ] = Depends(get_role_manager),
    ) -> list[role_schema]:
        # TODO Проверить права доступа у пользователя
        roles = await role_manager.search(page_params, filter_param)
        logging.info("success")
        return list(role_schema.from_orm(role) for role in roles)

    @router.post(
        "/roles",
        response_model=role_schema,
        status_code=status.HTTP_201_CREATED,
        summary="Create a role",
        description="Create a new item to the role directory",
        response_description="Role entity",
        dependencies=[Depends(get_current_adminuser)],
        tags=['Roles'],
    )
    async def create_role(  # pyright: ignore
        request: Request,
        role_create: role_create_schema,
        role_manager: BaseRoleManager[
            models_protocol.UP, models_protocol.RP, models_protocol.URP
        ] = Depends(get_role_manager),
    ) -> role_schema:
        # TODO Проверить права доступа у пользователя

        try:
            role = await role_manager.create(role_create, request=request)
            logging.info("success:%s" % role.id)
            return role_schema.from_orm(role)

        except exceptions.RoleAlreadyExists:
            logging.exception("RoleAlreadyExists:%s" %role_create)
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.UPDATE_ROLE_NAME_ALREADY_EXISTS,
            )

    @router.get(
        "/roles/{role_id}",
        response_model=role_schema,
        summary="Get a role",
        description="Get a item from the role directory",
        response_description="Role entity",
        dependencies=[Depends(get_current_adminuser)],
        tags=['Roles'],
    )
    async def get_role(  # pyright: ignore
        request: Request,
        role_id: UUID,
        role_manager: BaseRoleManager[
            models_protocol.UP, models_protocol.RP, models_protocol.URP
        ] = Depends(get_role_manager),
    ) -> role_schema:
        # TODO Проверить права доступа у пользователя
        try:
            role = await role_manager.get(role_id)
            logging.info("success:%s" % role_id)
            return role_schema.from_orm(role)

        except exceptions.RoleNotExists:
            logging.exception("RoleNotExists:%s" %role_id)
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=ErrorCode.ROLE_IS_NOT_EXISTS
            )

    @router.put(
        "/roles",
        response_model=role_schema,
        status_code=status.HTTP_201_CREATED,
        summary="Update a role",
        description="Update a role",
        response_description="Update role entity",
        dependencies=[Depends(get_current_adminuser)],
        tags=['Roles'],
    )
    async def update_role(  # pyright: ignore
        request: Request,
        role_update: role_update_schema,
        role_manager: BaseRoleManager[
            models_protocol.UP, models_protocol.RP, models_protocol.URP
        ] = Depends(get_role_manager),
    ) -> role_schema:
        try:
            # TODO Проверить доступ пользователя

            role = await role_manager.get(role_update.id)

            role = await role_manager.update(role_update, role, request=request)

            logging.info("success:%s" % role_update.id)
            return role_schema.from_orm(role)

        except exceptions.RoleNotExists:
            logging.exception("RoleNotExists:%s" % role_update)
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=ErrorCode.ROLE_IS_NOT_EXISTS
            )

        except exceptions.RoleAlreadyExists:
            logging.exception("RoleAlreadyExists:%s" % role_update)
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.UPDATE_ROLE_NAME_ALREADY_EXISTS,
            )

    @router.delete(
        "/roles/{role_id}",
        response_model=role_schema,
        status_code=status.HTTP_200_OK,
        summary="Delete a role",
        description="Delete a role",
        response_description="Deleted role entity",
        dependencies=[Depends(get_current_adminuser)],
        tags=['Roles'],
    )
    async def delete_role(  # pyright: ignore
        request: Request,
        role_id: UUID,
        role_manager: BaseRoleManager[
            models_protocol.UP, models_protocol.RP, models_protocol.URP
        ] = Depends(get_role_manager),
    ) -> role_schema:
        try:
            # TODO Проверить доступ пользователя

            role = await role_manager.get(role_id)

            role = await role_manager.delete(role, request=request)
            logging.info("success:%s" % role_id)
            return role_schema.from_orm(role)

        except exceptions.RoleNotExists:
            logging.exception("RoleNotExists:%s" % role_id)
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=ErrorCode.ROLE_IS_NOT_EXISTS
            )

    @router.get(
        "/users/roles",
        status_code=status.HTTP_200_OK,
        responses={
            status.HTTP_204_NO_CONTENT: {"description": "User have not role."},
            status.HTTP_404_NOT_FOUND: {"description": "User or role not found."},
        },
        summary="Check user role",
        description="Check if user is assigned to the role",
        dependencies=[Depends(get_current_adminuser)],
        tags=['Roles'],
    )
    async def check_user_role(  # pyright: ignore
        user_role: user_role_update_schema,
        user_manager: BaseUserManager[
            models_protocol.UP, models_protocol.SIHE
        ] = Depends(get_user_manager),
        role_manager: BaseRoleManager[
            models_protocol.UP, models_protocol.RP, models_protocol.URP
        ] = Depends(get_role_manager),
    ) -> None:
        try:
            # TODO Проверить доступ пользователя
            if not await user_manager.get(user_role.user_id):
                raise exceptions.UserNotExists

            if not await role_manager.check_user_role(user_role):
                raise exceptions.UserHaveNotRole
            
            logging.info("success:%s" % user_role)

        except exceptions.UserNotExists:
            logging.exception("UserNotExists:%s" %user_role)
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=ErrorCode.USER_IS_NOT_EXISTS
            )
        except exceptions.RoleNotExists:
            logging.exception("RoleNotExists:%s" %user_role)
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=ErrorCode.ROLE_IS_NOT_EXISTS
            )
        except exceptions.UserHaveNotRole:
            logging.exception("UserHaveNotRole:%s" %user_role)
            raise HTTPException(
                status.HTTP_204_NO_CONTENT, detail=ErrorCode.ROLE_IS_NOT_EXISTS
            )

    @router.post(
        "/users/roles",
        status_code=status.HTTP_201_CREATED,
        response_model=user_role_schema,
        summary="Assign a role",
        description="Assign a role to a user",
        dependencies=[Depends(get_current_adminuser)],
        tags=['Roles'],
    )
    async def assign_role(  # pyright: ignore
        user_role: user_role_update_schema,
        user_manager: BaseUserManager[
            models_protocol.UP, models_protocol.SIHE
        ] = Depends(get_user_manager),
        role_manager: BaseRoleManager[
            models_protocol.UP, models_protocol.RP, models_protocol.URP
        ] = Depends(get_role_manager),
    ) -> None:
        try:
            # TODO Проверить доступ пользователя
            if not await user_manager.get(user_role.user_id):
                raise exceptions.UserNotExists()

            if not await role_manager.get(user_role.role_id):
                raise exceptions.RoleNotExists()

            if await role_manager.check_user_role(user_role):
                raise exceptions.RoleAlreadyAssign()

            await role_manager.assign_user_role(user_role)

            logging.info("success:%s" % user_role)

        except exceptions.UserNotExists:
            logging.exception("UserNotExists:%s" %user_role)
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=ErrorCode.ROLE_IS_NOT_EXISTS
            )
        except exceptions.RoleNotExists:
            logging.exception("RoleNotExists:%s" %user_role)
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=ErrorCode.ROLE_IS_NOT_EXISTS
            )

    @router.delete(
        "/users/roles",
        status_code=status.HTTP_200_OK,
        responses={
            status.HTTP_204_NO_CONTENT: {"description": "User or role not found."}
        },
        summary="Unassign a role",
        description="Unassign user's role",
        response_description="Message entity",
        dependencies=[Depends(get_current_adminuser)],
        tags=['Roles'],
    )
    async def remove_user_role(  # pyright: ignore
        user_role: user_role_schema,
        user_manager: BaseUserManager[
            models_protocol.UP, models_protocol.SIHE
        ] = Depends(get_user_manager),
        role_manager: BaseRoleManager[
            models_protocol.UP, models_protocol.RP, models_protocol.URP
        ] = Depends(get_role_manager),
    ):
        try:
            # TODO Проверить доступ пользователя
            if not await user_manager.get(user_role.user_id):
                raise exceptions.UserNotExists()

            if not await role_manager.get(user_role.role_id):
                raise exceptions.RoleNotExists()

            await role_manager.remove_user_role(user_role.id)

            logging.info("success:%s" % user_role)

        except exceptions.UserNotExists:
            logging.exception("UserNotExists:%s" %user_role)
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=ErrorCode.ROLE_IS_NOT_EXISTS
            )
        except exceptions.RoleNotExists:
            logging.exception("RoleNotExists:%s" %user_role)
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=ErrorCode.ROLE_IS_NOT_EXISTS
            )

    @router.get(
        "/users/{user_id}/roles",
        response_model=list[UUID],
        summary="List the user's roles",
        description="Get list the user's roles",
        dependencies=[Depends(get_current_adminuser)],
        tags=['Roles'],
    )
    async def user_roles(  # pyright: ignore
        user_id: UUID,
        user_manager: BaseUserManager[
            models_protocol.UP, models_protocol.SIHE
        ] = Depends(get_user_manager),
        role_manager: BaseRoleManager[
            models_protocol.UP, models_protocol.RP, models_protocol.URP
        ] = Depends(get_role_manager),
    ) -> list[user_role_schema]:
        try:
            # TODO Проверить доступ пользователя
            user = await user_manager.get(user_id)
            roles = await role_manager.get_user_roles(user.id)

            logging.info("success:%s" % user_id)
            return list(user_role_schema.from_orm(role) for role in roles)

        except exceptions.UserNotExists:
            logging.exception("UserNotExists:%s" %user_id)
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=ErrorCode.ROLE_IS_NOT_EXISTS
            )

    return router
