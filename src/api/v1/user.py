from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT

import src.models.models as m
from core.pagination import PaginateQueryParams
from services.auth import get_auth_service
from src.services.abc import BaseUserService, BaseAuthService
from src.services.user import get_user_service


router = APIRouter()


@router.post(
    "/register",
    response_model=m.UserRegistrationParamsOut,
    summary="Register a new user",
    description="Register a new user in Movix-Auth service",
    response_description="",  # TODO fill response description
    tags=['Auth'],
)
async def register(
        params: m.UserRegistrationParamsIn,
        user_service: BaseUserService = Depends(get_user_service)
) -> m.UserRegistrationParamsOut:

    return await user_service.register(params)


@router.get(
    "/user",
    response_model=m.UserDetailed,
    summary="Get current user",
    description="Get sensitive data of current user",
    response_description="sensitive data",
    tags=['User'],
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
    response_model=m.UserSigninHistoryOut,
    summary="Get sign-in history",
    description="Get user's account sign-in history",
    response_description="list of sign-ins",
    tags=['User'],
)
async def sign_in_history(
    paginate_params: PaginateQueryParams,
    user_service: BaseUserService = Depends(get_user_service),
    auth_service: BaseAuthService = Depends(get_auth_service),
) -> m.UserSigninHistoryOut:
    # TODO Проверить валидность токена
    # TODO Получить из токена данные пользователя
    user = None

    return await user_service.get_sign_in_history(user, paginate_params)
