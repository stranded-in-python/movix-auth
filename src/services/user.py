from uuid import UUID

from .abc import BaseUserService
import models.models as m


class UserService(BaseUserService):
    async def register(
            self,
            params: m.UserRegistrationParamsIn
    ) -> m.UserRegistrationParamsOut:

        return m.UserRegistrationParamsOut(id="121", **params)

    async def get(self, user_id: UUID) -> m.UserDetailed:
        return m.UserDetailed(
            **{
                "id": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff",
                "username": "AlanX9",
                "email": "",
                "first_name": "Alan",
                "last_name": "Baxterman"
            }
        )  # Получить из хранилища данные пользователя

    async def change_password(self, params: m.UserUpdateIn):
        return m.UserUpdateOut()


def get_user_service() -> UserService:
    return UserService()
