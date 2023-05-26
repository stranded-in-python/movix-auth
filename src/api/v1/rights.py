from fastapi import APIRouter, status

import models as models
from core.pagination import PaginateQueryParams

router = APIRouter()


@router.post(
    "/rights",
    response_model=models.ARP,
    summary="Create a access right",
    description="Create a new item to the access rights directory",
    response_description="Access right entity",
    tags=['Access right'],
)
async def create_access(params: models.ARP) -> models.ARP:
    ...


@router.get(
    "/rights",
    response_model=list[models.ARP],
    summary="View all access rights",
    description="View all access rights",
    response_description="Access entities",
    tags=['Access right'],
)
async def get_all(pag_params: PaginateQueryParams) -> list[models.ARP]:
    ...


@router.put(
    "/rights/{access_right_id}",
    response_model=models.ARP,
    summary="Change a access right",
    description="Change a access right",
    response_description="Changed access right entity",
    tags=['Access right'],
)
async def update_access_right(access_right_id: models.ID) -> models.ARP:
    ...


@router.delete(
    "/rights/{access_right_id}",
    response_model=models.ARP,
    summary="Delete a access right",
    description="Delete a access right",
    response_description="Deleted access right entity",
    tags=['Access right'],
)
async def delete_role(access_right_id: models.ID) -> models.ARP:
    ...


@router.get(
    "/roles/{roles_id}/rights/{access_right_id}",
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Role have not access right.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Role or access right not found.",
        },
    },
    summary="Check roles access right",
    description="Check if role is assigned to the access right",
    response_description="Message entity",
    tags=['Access right'],
)
async def check_access_right(roles_id: models.ID, access_right_id: models.ID) -> None:
    ...


@router.post(
    "/roles/{roles_id}/rights/{access_right_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Assign a access right",
    description="Assign a access right to a role",
    response_description="Message entity",
    tags=['Access right'],
)
async def assign_access_right(roles_id: models.ID, access_right_id: models.ID) -> None:
    ...


@router.delete(
    "/roles/{roles_id}/rights/{access_right_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Role or access right not found.",
        },
    },
    summary="Unassign a access right",
    description="Unassign role's access right",
    response_description="Message entity",
    tags=['Access right'],
)
async def unassign_access_right(roles_id: models.ID, access_right_id: models.ID) -> None:
    ...


@router.get(
    "/roles/{roles_id}/rights",
    response_model=list[models.ARP],
    summary="List the role's access right",
    description="Get list the role's access right",
    response_description="Message entity",
    tags=['Access right'],
)
async def get_role_rights(roles_id: models.ID) -> list[models.ARP]:
    ...
