from fastapi import APIRouter

import models.models as m
from core.pagination import PaginateQueryParams

router = APIRouter()


@router.post(
    "/rights",
    response_model=m.AccessOut,
    summary="Create a access right",
    description="Create a new item to the access rights directory",
    response_description="Access right entity",
    tags=['Access right'],
)
async def create_access(params: m.AccessIn) -> m.AccessOut:
    ...


@router.get(
    "/rights",
    response_model=list[m.AccessRightOut],
    summary="View all access rights",
    description="View all access rights",
    response_description="Access entities",
    tags=['Access right'],
)
async def get_all(pag_params: PaginateQueryParams) -> list[m.AccessRightOut]:
    ...


@router.put(
    "/rights/{access_right_id}",
    response_model=m.AccessRightOut,
    summary="Change a access right",
    description="Change a access right",
    response_description="Changed access right entity",
    tags=['Access right'],
)
async def update_access_right(access_right_id: int) -> m.AccessRightOut:
    ...


@router.delete(
    "/rights/{access_right_id}",
    response_model=m.AccessRightOut,
    summary="Delete a access right",
    description="Delete a access right",
    response_description="Deleted access right entity",
    tags=['Access right'],
)
async def delete_role(access_right_id: int) -> m.AccessRightOut:
    ...


@router.get(
    "/roles/{roles_id}/rights/{access_right_id}",
    response_model=m.Message,
    summary="Check roles access right",
    description="Check if role is assigned to the access right",
    response_description="Message entity",
    tags=['Access right'],
)
async def check_access_right(roles_id: int, access_right_id: int) -> m.Message:
    ...


@router.post(
    "/roles/{roles_id}/rights/{access_right_id}",
    response_model=m.Message,
    summary="Assign a access right",
    description="Assign a access right to a role",
    response_description="Message entity",
    tags=['Access right'],
)
async def assign_access_right(roles_id: int, access_right_id: int) -> m.Message:
    ...


@router.delete(
    "/roles/{roles_id}/rights/{access_right_id}",
    response_model=m.Message,
    summary="Unassign a access right",
    description="Unassign role's access right",
    response_description="Message entity",
    tags=['Access right'],
)
async def unassign_access_right(roles_id: int, access_right_id: int) -> m.Message:
    ...


@router.get(
    "/roles/{roles_id}/rights",
    response_model=list[m.AccessRightOut],
    summary="List the role's access right",
    description="Get list the role's access right",
    response_description="Message entity",
    tags=['Access right'],
)
async def get_role_rights(roles_id: int) -> list[m.AccessRightOut]:
    ...
