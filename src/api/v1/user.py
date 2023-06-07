from typing import Type

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

import core.exceptions as exceptions
from api import schemas
from api.v1.common import ErrorCode, ErrorModel
from authentication import Authenticator
from core.pagination import PaginateQueryParams
from db import models_protocol
from managers.user import BaseUserManager, UserManagerDependency


def get_users_me_router(
    get_user_manager: UserManagerDependency[
        models_protocol.UP, models_protocol.SIHE
    ],
    user_schema: Type[schemas.U],
    user_update_schema: Type[schemas.UU],
    event_schema: Type[schemas.EventRead],
    authenticator: Authenticator[models_protocol.UP, models_protocol.SIHE],
) -> APIRouter:
    router = APIRouter()
    router.prefix = "/api/v1/users/me"

    get_current_active_user = authenticator.current_user(active=True)

    @router.get(
        "",
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
        "",
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
        "",
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


def get_users_router(
    get_user_manager: UserManagerDependency[models_protocol.UP, models_protocol.SIHE],
    user_schema: Type[schemas.U],
    user_update_schema: Type[schemas.UU],
    authenticator: Authenticator[models_protocol.UP, models_protocol.SIHE],
) -> APIRouter:
    router = APIRouter()
    router.prefix = "/api/v1/users"

    get_current_superuser = authenticator.current_user(
        active=True, superuser=True
    )

    async def get_user_or_404(
        id: str,
        user_manager: BaseUserManager[models_protocol.UP, models_protocol.SIHE] = Depends(get_user_manager),
    ) -> models_protocol.UP:
        try:
            parsed_id = user_manager.parse_id(id)
            return await user_manager.get(parsed_id)
        except (exceptions.UserNotExists, exceptions.InvalidID) as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e

    @router.get(
        "/{id}",
        response_model=user_schema,
        dependencies=[Depends(get_current_superuser)],
        name="users:user",
        responses={
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Missing token or inactive user.",
            },
            status.HTTP_403_FORBIDDEN: {
                "description": "Not a superuser.",
            },
            status.HTTP_404_NOT_FOUND: {
                "description": "The user does not exist.",
            },
        },
    )
    async def get_user(  # pyright: ignore
        user: models_protocol.UP = Depends(get_user_or_404)
    ):
        return user_schema.from_orm(user)

    @router.patch(
        "/{id}",
        response_model=user_schema,
        dependencies=[Depends(get_current_superuser)],
        name="users:patch_user",
        responses={
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Missing token or inactive user.",
            },
            status.HTTP_403_FORBIDDEN: {
                "description": "Not a superuser.",
            },
            status.HTTP_404_NOT_FOUND: {
                "description": "The user does not exist.",
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
    )
    async def update_user(  # pyright: ignore
        user_update: user_update_schema,  # type: ignore
        request: Request,
        user: models_protocol.UP = Depends(get_user_or_404),
        user_manager: BaseUserManager[models_protocol.UP, models_protocol.SIHE] = Depends(get_user_manager),
    ):
        try:
            user = await user_manager.update(
                user_update, user, safe=False, request=request
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

    @router.delete(
        "/{id}",
        status_code=status.HTTP_204_NO_CONTENT,
        response_class=Response,
        dependencies=[Depends(get_current_superuser)],
        name="users:delete_user",
        responses={
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Missing token or inactive user.",
            },
            status.HTTP_403_FORBIDDEN: {
                "description": "Not a superuser.",
            },
            status.HTTP_404_NOT_FOUND: {
                "description": "The user does not exist.",
            },
        },
    )
    async def delete_user(  # pyright: ignore
        user: models_protocol.UP = Depends(get_user_or_404),
        user_manager: BaseUserManager[models_protocol.UP, models_protocol.SIHE] = Depends(get_user_manager),
    ):
        await user_manager.delete(user)
        return None

    return router
