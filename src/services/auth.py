from flask_jwt_extended import create_access_token

import src.models.models as m
from src.services.abc import BaseAuthService


class AuthService(BaseAuthService):
    def register(self, params: m.UserRegistrationParamsIn) -> None:
        return

    def login(self, params: m.LoginParamsIn) -> m.LoginParamsOut:
        user_id = params.username # Заменить на получение id из базы

        return m.LoginParamsOut(
            access_token=create_access_token(identity=user_id),
            refresh_token="refresh_token"
        )

    def logout(self, params: m.UserPayload) -> None:
        ...
