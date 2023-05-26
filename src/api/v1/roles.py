from typing import Type
from uuid import UUID

from fastapi import APIRouter, Depends, status

import models as models
import schemas
from authentication import Authenticator
from core.pagination import PaginateQueryParams
from services.user import UserManagerDependency


def get_roles_router(
    get_user_manager: UserManagerDependency[models.UP, models.ID],
    role_schema: Type[schemas.R],
    role_update_schema: Type[schemas.RU],
    authenticator: Authenticator
) -> APIRouter:

    router = APIRouter()
    router.prefix = "/api/v1"

    get_current_active_user = authenticator.current_user(
        active=True
    )

    @router.post(
        "/roles",
        response_model=role_schema,
        summary="Create a role",
        description="Create a new item to the role directory",
        response_description="Role entity",
        tags=['Roles'],
    )
    async def create_role(params: role_update_schema) -> role_schema:
        ...


    @router.get(
        "/roles",
        response_model=list[role_schema],
        summary="View all roles",
        description="View all roles",
        response_description="Role entities",
        tags=['Roles'],
    )
    async def get_all(pag_params: PaginateQueryParams = Depends(PaginateQueryParams)) -> list[role_schema]:
        ...


    @router.put(
        "/roles/{role_id}",
        response_model=role_schema,
        summary="Change a role",
        description="Change a role",
        response_description="Changed role entity",
        tags=['Roles'],
    )
    async def update_role(role_id: UUID, params: role_update_schema) -> role_schema:
        ...


    @router.delete(
        "/roles/{role_id}",
        response_model=role_schema,
        summary="Delete a role",
        description="Delete a role",
        response_description="Deleted role entity",
        tags=['Roles'],
    )
    async def delete_role(role_id: models.ID) -> role_schema:
        ...


    @router.get(
        "/users/{user_id}/roles/{role_id}",
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
    async def check_role(user_id: UUID, role_id: UUID) -> None:
        ...


    @router.post(
        "/users/{user_id}/roles/{role_id}",
        status_code=status.HTTP_201_CREATED,
        summary="Assign a role",
        description="Assign a role to a user",
        tags=['Roles'],
    )
    async def assign_role(user_id: UUID, role_id: UUID) -> None:
        ...


    @router.delete(
        "/users/{user_id}/roles/{role_id}",
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
    async def unassign_role(user_id: UUID, role_id: UUID) -> None:
        ...


    @router.get(
        "/users/{user_id}/roles",
        response_model=list[role_schema],
        summary="List the user's roles",
        description="Get list the user's roles",
        tags=['Roles'],
    )
    async def user_roles(user_id: UUID) -> list[role_schema]:
        ...

    return router
