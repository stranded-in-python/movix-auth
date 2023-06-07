from typing import Type

from fastapi import APIRouter, Depends, HTTPException, Request, status

import core.exceptions as exceptions
from api import schemas
from api.v1.common import ErrorCode, ErrorModel
from authentication import Authenticator
from core.pagination import PaginateQueryParams
from db import models_protocol
from managers.user import BaseUserManager, UserManagerDependency


def get_users_router(
    get_user_manager: UserManagerDependency[
        models_protocol.UP, models_protocol.SIHE
    ],
    user_schema: Type[schemas.U],
    user_update_schema: Type[schemas.UU],
    event_schema: Type[schemas.EventRead],
    authenticator: Authenticator[models_protocol.UP, models_protocol.SIHE],
) -> APIRouter:
    router = APIRouter()
    router.prefix = "/api/v1"

    get_current_active_user = authenticator.current_user(active=True)

    @router.get(
        "/users/me",
        response_model=user_schema,
        dependencies=[Depends(get_current_active_user)],
        name="users:current_user",
        summary="Get current user",
        description="Get sensitive data of current user",
        response_description="sensitive data",
        tags=['User'],
        responses={
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Missing token or inactive user."
            }
        },
    )
    async def get_current_user(  # pyright: ignore
        user: models_protocol.UP = Depends(get_current_active_user),
    ) -> schemas.UserRead:
        return user_schema.from_orm(user)

    @router.put(
        "/users/me",
        response_model=user_schema,
        dependencies=[Depends(get_current_active_user)],
        name="users:patch_current_user",
        summary="Update current user",
        description="Update sensitive data of current user",
        response_description="sensitive data",
        responses={
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Missing token or inactive user."
            },
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS: {
                                "summary": "A user with this email already exists.",
                                "value": {
                                    "detail": ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS
                                },
                            },
                            ErrorCode.UPDATE_USER_INVALID_PASSWORD: {
                                "summary": "Password validation failed.",
                                "value": {
                                    "detail": {
                                        "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                                        "reason": "Password should be"
                                        "at least 3 characters",
                                    }
                                },
                            },
                        }
                    }
                },
            },
        },
        tags=['User'],
    )
    async def update_current_user(  # pyright: ignore
        request: Request,
        user_update: user_update_schema,
        user: models_protocol.UP = Depends(get_current_active_user),
        user_manager: BaseUserManager[models_protocol.UP, models_protocol.SIHE] = Depends(get_user_manager),
    ) -> schemas.UserRead:
        try:
            user = await user_manager.update(
                user_update, user, safe=True, request=request
            )
            return user_schema.from_orm(user)

        except exceptions.InvalidPasswordException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )

        except exceptions.UserAlreadyExists:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS,
            )

    @router.get(
        "/users/me/sign-in-history",
        response_model=list[schemas.BaseSignInHistoryEvent],
        summary="Get sign-in history",
        description="Get user's account sign-in history",
        response_description="list of sign-ins",
        tags=['User'],
    )
    async def sign_in_history(  # pyright: ignore
        user_manager: BaseUserManager[models_protocol.UP, models_protocol.SIHE] = Depends(get_user_manager),
        user: models_protocol.UP = Depends(get_current_active_user),
        paginate_params: PaginateQueryParams = Depends(PaginateQueryParams),
    ) -> list[event_schema]:
        events = await user_manager.get_sign_in_history(user, paginate_params)

        return list(event_schema.from_orm(event) for event in events)

    return router
