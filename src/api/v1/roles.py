from fastapi import APIRouter

import models.models as m
from core.pagination import PaginateQueryParams

router = APIRouter()


@router.post(
    "/roles",
    response_model=m.RoleOut,
    summary="Create a role",
    description="Create a new item to the role directory",
    response_description="Role entity",
    tags=['Roles'],
)
async def create_role(params: m.RoleIn) -> m.RoleOut:
    ...


@router.get(
    "/roles",
    response_model=list[m.RoleOut],
    summary="View all roles",
    description="View all roles",
    response_description="Role entities",
    tags=['Roles'],
)
async def get_all(pag_params: PaginateQueryParams) -> list[m.RoleOut]:
    ...


@router.put(
    "/roles/{role_id}",
    response_model=m.RoleOut,
    summary="Change a role",
    description="Change a role",
    response_description="Changed role entity",
    tags=['Roles'],
)
async def update_role(role_id: int) -> m.RoleOut:
    ...


@router.delete(
    "/roles/{role_id}",
    response_model=m.RoleOut,
    summary="Delete a role",
    description="Delete a role",
    response_description="Deleted role entity",
    tags=['Roles'],
)
async def delete_role(role_id: int) -> m.RoleOut:
    ...


@router.get(
    "/users/{user_id}/roles/{role_id}",
    response_model=m.Message,
    summary="Check user role",
    description="Check if user is assigned to the role",
    response_description="Message entity",
    tags=['Roles'],
)
async def check_role(user_id: int, role_id: int) -> m.Message:
    ...


@router.post(
    "/users/{user_id}/roles/{role_id}",
    response_model=m.Message,
    summary="Assign a role",
    description="Assign a role to a user",
    response_description="Message entity",
    tags=['Roles'],
)
async def assign_role(user_id: int, role_id: int) -> m.Message:
    ...


@router.delete(
    "/users/{user_id}/roles/{role_id}",
    response_model=m.Message,
    summary="Unassign a role",
    description="Unassign user's role",
    response_description="Message entity",
    tags=['Roles'],
)
async def unassign_role(user_id: int, role_id: int) -> m.Message:
    ...


@router.get(
    "/users/{user_id}/roles",
    response_model=list[m.RoleOut],
    summary="List the user's roles",
    description="Get list the user's roles",
    response_description="Message entity",
    tags=['Roles'],
)
async def user_roles(user_id: int) -> list[m.RoleOut]:
    ...
