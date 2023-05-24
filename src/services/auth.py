from functools import lru_cache

from fastapi_jwt_auth import AuthJWT

import models as m
from services.abc import BaseAuthService


class AuthService(BaseAuthService):
    def __init__(self, jwt_manager: AuthJWT):
        self.jwt_manager = jwt_manager()

    async def login(self, params: m.LoginParamsIn) -> m.LoginParamsOut:
        user_id = params.username # Заменить на получение id из базы

        return m.LoginParamsOut(
            access_token=self.jwt_manager.create_access_token(subject=user_id),
            refresh_token="refresh_token"
        )

    async def logout(self, params: m.UserPayload) -> None:
        ...

    async def refresh_token(self, refresh_token) -> m.TokenPair:
        ...

@lru_cache
def get_auth_service() -> AuthService:
    return AuthService(jwt_manager=AuthJWT)
