from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from api.v1.common import ErrorCode, ErrorModel
from authentication import AuthenticationBackend, Authenticator, Strategy
from db import models_protocol
from managers.user import BaseUserManager, UserManagerDependency
from openapi import OpenAPIResponseType


def get_auth_router(
    access_backend: AuthenticationBackend[models_protocol.UP, models_protocol.SIHE],
    refresh_backend: AuthenticationBackend[models_protocol.UP, models_protocol.SIHE],
    get_user_manager: UserManagerDependency[
        models_protocol.UP,
        models_protocol.SIHE,
        models_protocol.OAP,
        models_protocol.UOAP,
    ],
    access_authenticator: Authenticator[models_protocol.UP, models_protocol.SIHE],
    refresh_authenticator: Authenticator[models_protocol.UP, models_protocol.SIHE],
    requires_verification: bool = False,
) -> APIRouter:
    """Generate a router with login/logout routes for an authentication backend."""
    router = APIRouter()
    router.prefix = "/api/v1"

    get_current_user_token = access_authenticator.current_user_token(active=True)
    get_current_user_refresh_token = refresh_authenticator.current_user_token(
        active=True
    )

    login_responses: OpenAPIResponseType = {
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.LOGIN_BAD_CREDENTIALS: {
                            "summary": "Bad credentials or the user is inactive.",
                            "value": {"detail": ErrorCode.LOGIN_BAD_CREDENTIALS},
                        }
                    }
                }
            },
        },
        **access_backend.transport.get_openapi_login_responses_success(),
    }

    @router.post(
        "/login", name=f"auth:{access_backend.name}.login", responses=login_responses
    )
    async def login(  # pyright: ignore
        request: Request,
        credentials: OAuth2PasswordRequestForm = Depends(),
        user_manager: BaseUserManager[
            models_protocol.UP,
            models_protocol.SIHE,
            models_protocol.OAP,
            models_protocol.UOAP,
        ] = Depends(get_user_manager),
        strategy: Strategy[models_protocol.UP, models_protocol.SIHE] = Depends(
            refresh_backend.get_strategy
        ),
    ):
        user = await user_manager.authenticate(credentials)

        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
            )
        response = await refresh_backend.login(strategy, user)
        await user_manager.on_after_login(user, request, response)
        return response

    @router.post(
        "/refresh",
        name=f"auth:{access_backend.name}.refresh",
        responses=login_responses,
    )
    async def refresh(  # pyright: ignore
        user_token: tuple[models_protocol.UP, str] = Depends(
            get_current_user_refresh_token
        ),
        strategy: Strategy[models_protocol.UP, models_protocol.SIHE] = Depends(
            access_backend.get_strategy
        ),
    ):
        if not user_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ErrorCode.REFRESH_BAD_TOKEN,
            )
        user, _ = user_token

        response = await access_backend.login(strategy, user)
        return response

    logout_responses: OpenAPIResponseType = {
        **{
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Missing token or inactive user."
            }
        },
        **access_backend.transport.get_openapi_logout_responses_success(),
    }

    @router.post(
        "/blacklist",
        name=f"auth:{access_backend.name}.blacklist",
        responses=logout_responses,
    )
    async def blacklist(  # pyright: ignore
        user_token: tuple[models_protocol.UP, str] = Depends(get_current_user_token),
        strategy: Strategy[models_protocol.UP, models_protocol.SIHE] = Depends(
            access_backend.get_strategy
        ),
    ):
        if not user_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ErrorCode.ACCESS_BAD_TOKEN,
            )
        user, token = user_token
        return await access_backend.logout(strategy, user, token)

    @router.post(
        "/logout", name=f"auth:{access_backend.name}.logout", responses=logout_responses
    )
    async def logout(  # pyright: ignore
        user_token: tuple[models_protocol.UP, str] = Depends(
            get_current_user_refresh_token
        ),
        strategy: Strategy[models_protocol.UP, models_protocol.SIHE] = Depends(
            refresh_backend.get_strategy
        ),
    ):
        if not user_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ErrorCode.REFRESH_BAD_TOKEN,
            )
        user, token = user_token
        return await refresh_backend.logout(strategy, user, token)

    return router
