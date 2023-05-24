from fastapi import APIRouter, Depends

import models as m
from services.abc import BaseAuthService
from services.auth import get_auth_service

router = APIRouter()


@router.post(
    "/login",
    response_model=m.LoginParamsOut,
    summary="Login to the account",
    description="Login to the account of Movix-Auth",
    response_description="login, password",
    tags=['Auth'],
)
async def login(
        params: m.LoginParamsIn,
        auth_service: BaseAuthService = Depends(get_auth_service)
) -> m.LoginParamsOut:
    return await auth_service.login(params)


@router.post(
    "/logout",
    response_model=m.LogoutParamsOut,
    summary="Login to the account",
    description="Login to the account of Movix-Auth",
    response_description="login, password",
    tags=['Auth'],
)
async def logout(
    auth_service: BaseAuthService = Depends(get_auth_service)
) -> m.LogoutParamsOut:
    """Logout of the account"""
    current_user = m.UserPayload()

    return auth_service.logout(current_user)


@router.post(
    "/token/refresh",
    response_model=m.LogoutParamsOut,
    summary="Refresh access token",
    description="Refresh access token",
    response_description="Refresh token",
    tags=['Auth'],
)
async def refresh(
        refresh_token: str,
        auth_service: BaseAuthService = Depends(get_auth_service)
) -> m.TokenPair:
    return auth_service.refresh_token(refresh_token)
