from typing import Type
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request

import models as models
import schemas as schemas
from app.schemas import ID
from authentication import Authenticator
from core import exceptions
from core.pagination import PaginateQueryParams
from services.role import RoleManagerDependency, BaseRoleManager
from services.user import UserManagerDependency, BaseUserManager

from api.v1.common import ErrorCode


def get_roles_router(
    get_user_manager: UserManagerDependency[models.UP, models.ID],
    get_role_manager: RoleManagerDependency[models.RP, models.ID],
    role_schema: Type[schemas.R],
    role_create_schema: Type[schemas.RC],
    role_update_schema: Type[schemas.RU],
    user_role_schema: Type[schemas.UR],
    user_role_update_schema: Type[schemas.UR],
    authenticator: Authenticator
) -> APIRouter:

    router = APIRouter()
    router.prefix = "/api/v1"

    get_current_active_user = authenticator.current_user(
        active=True
    )

    @router.get(
        "/roles/search",
        response_model=list[role_schema],
        summary="View all roles",
        description="View all roles",
        response_description="Role entities",
        tags=['Roles'],
    )
    async def search(
            page_params: PaginateQueryParams = Depends(PaginateQueryParams),
            filter_param: str | None = None,
            role_manager: BaseRoleManager[models.RP, models.ID] = Depends(get_role_manager),
    ) -> list[role_schema]:

        # TODO Проверить права доступа у пользователя

        return list(
            role_schema.from_orm(role[0])
            for role in await role_manager.search(page_params, filter_param)
        )

    @router.post(
        "/roles",
        response_model=role_schema,
        status_code=status.HTTP_201_CREATED,
        summary="Create a role",
        description="Create a new item to the role directory",
        response_description="Role entity",
        tags=['Roles'],
    )
    async def create_role(
            request: Request,
            role_create: role_create_schema,
            role_manager: BaseRoleManager[models.RP, models.ID] = Depends(get_role_manager),
    ) -> role_schema:
        # TODO Проверить права доступа у пользователя

        try:
            role = await role_manager.create(
                role_create, request=request
            )
            return role_schema.from_orm(role)

        except exceptions.RoleAlreadyExists:
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
        tags=['Roles'],
    )
    async def get_role(
            role_id: UUID,
            role_manager: BaseRoleManager[models.RP, models.ID] = Depends(get_role_manager),
    ) -> role_schema:
        # TODO Проверить права доступа у пользователя
        try:
            role = await role_manager.get(role_id)
            return role_schema.from_orm(role)

        except exceptions.RoleNotExists:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=ErrorCode.ROLE_IS_NOT_EXISTS,
            )

    @router.put(
        "/roles",
        response_model=role_schema,
        status_code=status.HTTP_201_CREATED,
        summary="Update a role",
        description="Update a role",
        response_description="Update role entity",
        tags=['Roles'],
    )
    async def update_role(
            request: Request,
            role_update: role_update_schema,
            role_manager: BaseRoleManager[models.RP, models.ID] = Depends(get_role_manager),
    ) -> role_schema:
        try:
            # TODO Проверить доступ пользователя

            role = await role_manager.get(role_update.id)

            role = await role_manager.update(
                role_update, role, request=request
            )
            return role_schema.from_orm(role)

        except exceptions.RoleNotExists:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS,
            )

        except exceptions.RoleAlreadyExists:
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
        tags=['Roles'],
    )
    async def delete_role(
            request: Request,
            role_id: UUID,
            role_manager: BaseRoleManager[models.RP, models.ID] = Depends(get_role_manager),
    ) -> role_schema:
        try:
            # TODO Проверить доступ пользователя

            role = await role_manager.get(role_id)

            role = await role_manager.delete(
                role, request=request
            )
            return role_schema.from_orm(role)

        except exceptions.RoleNotExists:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=ErrorCode.ROLE_IS_NOT_EXISTS,
            )

    @router.get(
        "/users/roles",
        status_code=status.HTTP_200_OK,
        responses={
            status.HTTP_204_NO_CONTENT: {
                "description": "User have not role.",
            },
            status.HTTP_404_NOT_FOUND: {
                "description": "User or role not found.",
            },
        },
        summary="Check user role",
        description="Check if user is assigned to the role",
        tags=['Roles'],
    )
    async def check_user_role(
            user_role: user_role_update_schema,
            user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
            role_manager: BaseRoleManager[models.RP, models.ID] = Depends(get_role_manager),
    ) -> None:
        try:
            # TODO Проверить доступ пользователя
            user = await user_manager.get(user_role.user_id)

            if not await role_manager.check_user_role(user_role):
                raise exceptions.UserHaveNotRole

        except exceptions.UserNotExists:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=ErrorCode.USER_IS_NOT_EXISTS,
            )
        except exceptions.RoleNotExists:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=ErrorCode.ROLE_IS_NOT_EXISTS,
            )
        except exceptions.UserHaveNotRole:
            raise HTTPException(
                status.HTTP_204_NO_CONTENT,
                detail=ErrorCode.ROLE_IS_NOT_EXISTS,
            )

    @router.post(
        "/users/roles",
        status_code=status.HTTP_201_CREATED,
        response_model=user_role_schema,
        summary="Assign a role",
        description="Assign a role to a user",
        tags=['Roles'],
    )
    async def assign_role(
            user_role: user_role_update_schema,
            user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
            role_manager: BaseRoleManager[models.RP, models.ID] = Depends(get_role_manager),
    ) -> None:
        try:
            # TODO Проверить доступ пользователя
            if not await user_manager.get(user_role.user_id):
                raise exceptions.UserNotExists()

            if not await role_manager.get(user_role.role_id):
                raise exceptions.RoleNotExists()

            if await role_manager.check_user_role(user_role):
                raise exceptions.RoleAlreadyAssign()

            return await role_manager.assign_user_role(user_role)

        except exceptions.UserNotExists:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=ErrorCode.ROLE_IS_NOT_EXISTS,
            )
        except exceptions.RoleNotExists:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=ErrorCode.ROLE_IS_NOT_EXISTS,
            )

    @router.delete(
        "/users/roles",
        status_code=status.HTTP_200_OK,
        responses={
            status.HTTP_204_NO_CONTENT: {
                "description": "User or role not found.",
            },
        },
        summary="Unassign a role",
        description="Unassign user's role",
        response_description="Message entity",
        tags=['Roles'],
    )
    async def remove_user_role(
            user_role: user_role_update_schema,
            user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
            role_manager: BaseRoleManager[models.RP, models.ID] = Depends(get_role_manager),
    ):
        try:
            # TODO Проверить доступ пользователя
            if not await user_manager.get(user_role.user_id):
                raise exceptions.UserNotExists()

            if not await role_manager.get(user_role.role_id):
                raise exceptions.RoleNotExists()

            await role_manager.remove_user_role(user_role)

        except exceptions.UserNotExists:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=ErrorCode.ROLE_IS_NOT_EXISTS,
            )
        except exceptions.RoleNotExists:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=ErrorCode.ROLE_IS_NOT_EXISTS,
            )

    @router.get(
        "/users/{user_id}/roles",
        response_model=list[UUID],
        summary="List the user's roles",
        description="Get list the user's roles",
        tags=['Roles'],
    )
    async def user_roles(
            user_id: UUID,
            user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
            role_manager: BaseRoleManager[models.RP, models.ID] = Depends(get_role_manager),
    ) -> list[UUID]:
        try:
            # TODO Проверить доступ пользователя
            user = await user_manager.get(user_id)

            _user_roles = await role_manager.get_user_roles(user.id)

            return list(
                user_role_schema.from_orm(role_id[0]).id
                for role_id in
                _user_roles
            )

        except exceptions.UserNotExists:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=ErrorCode.ROLE_IS_NOT_EXISTS,
            )

    return router
