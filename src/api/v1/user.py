from http import HTTPStatus
from typing import Type

from fastapi import APIRouter, Depends, status
from fastapi_jwt_auth import AuthJWT

import models as m
import schemas as schemas
from core.pagination import PaginateQueryParams
from services.auth import get_auth_service
from services.abc import BaseUserService, BaseAuthService
from services.user import UserServiceDependency
from authentication import Authenticator


def get_users_router(
    get_user_service: UserServiceDependency[m.UP, m.ID],
    authenticator: Authenticator,
    user_schema: Type[schemas.U] = schemas.U,
    user_update_schema: Type[schemas.UU] = schemas.UU,
    requires_verification: bool = False,
) -> APIRouter:

    router = APIRouter()

    @router.get(
        "/user",
        response_model=schemas.U,
        name="users:current_user",
        summary="Get current user",
        description="Get sensitive data of current user",
        response_description="sensitive data",
        tags=['User'],
        responses={
                status.HTTP_401_UNAUTHORIZED: {
                    "description": "Missing token or inactive user.",
                },
            },
    )
    async def get_current_user(
        user_service: BaseUserService = Depends(get_user_service),
        auth_service: BaseAuthService = Depends(get_auth_service),
        jwt_manager: AuthJWT = Depends()
    ) -> m.UserDetailed:

        jwt_manager.jwt_required()

        current_user = m.UserPayload(id=jwt_manager.get_jwt_subject())   # Получить из payload идентификатор

        return await user_service.get(current_user.id)


    @router.put(
        "/user",
        response_model=m.UserUpdateOut,
        summary="Update current user",
        description="Update sensitive data of current user",
        response_description="sensitive data",
        tags=['User'],
    )
    async def change_password_of_current_user(
        params: m.UserUpdateIn,
        user_service: BaseUserService = Depends(get_user_service),
        auth_service: BaseAuthService = Depends(get_auth_service)
    ) -> m.UserUpdateOut:

        return await user_service.change_password(params)


    @router.get(
        "/user/sign-in-history",
        response_model=list[schemas.UserSigninHistoryEvent],
        summary="Get sign-in history",
        description="Get user's account sign-in history",
        response_description="list of sign-ins",
        tags=['User'],
    )
    async def sign_in_history(
        paginate_params: PaginateQueryParams = Depends(PaginateQueryParams),
        user_service: BaseUserService = Depends(get_user_service),
        auth_service: BaseAuthService = Depends(get_auth_service),
    ) -> list[schemas.UserSigninHistoryEvent]:
        # TODO Проверить валидность токена
        # TODO Получить из токена данные пользователя
        user = None

        return await user_service.get_sign_in_history(user, paginate_params)

    return router
