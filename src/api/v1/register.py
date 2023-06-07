from typing import Type

from fastapi import APIRouter, Depends, HTTPException, Request, status

from api import schemas
import core.exceptions as ex
from api.v1.common import ErrorCode, ErrorModel
from db import models_protocol
from managers.user import BaseUserManager, UserManagerDependency


def get_register_router(
    get_user_manager: UserManagerDependency[
        models_protocol.UP, models_protocol.SIHE
    ],
    user_schema: Type[schemas.U],
    user_create_schema: Type[schemas.UC],
) -> APIRouter:
    """Generate a router with the register route."""
    router = APIRouter()
    router.prefix = "/api/v1"

    @router.post(
        "/register",
        response_model=user_schema,
        status_code=status.HTTP_201_CREATED,
        summary="Register a new user",
        description="Register a new user in Movix-Auth service",
        response_description="Short representation of created user",
        tags=['Register'],
        responses={
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.REGISTER_USER_ALREADY_EXISTS: {
                                "summary": "A user with this email already exists.",
                                "value": {
                                    "detail": ErrorCode.REGISTER_USER_ALREADY_EXISTS
                                },
                            },
                            ErrorCode.REGISTER_INVALID_PASSWORD: {
                                "summary": "Password validation failed.",
                                "value": {
                                    "detail": {
                                        "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                                        "reason": "Password should be"
                                        "at least 8 characters",
                                    }
                                },
                            },
                        }
                    }
                },
            }
        },
    )
    async def register(  # pyright: ignore
        request: Request,
        user_create: user_create_schema,
        user_service: BaseUserManager[models_protocol.UP, models_protocol.SIHE] = Depends(get_user_manager),
    ) -> user_schema:
        try:
            created_user = await user_service.create(
                user_create, safe=True, request=request
            )
        except ex.UserAlreadyExists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
            )
        except ex.InvalidPasswordException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )

        return user_schema.from_orm(created_user)

    return router
