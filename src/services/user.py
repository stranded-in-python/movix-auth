from uuid import UUID

from .abc import BaseUserService
from ..models.models import UserDetailed


class UserService(BaseUserService):
    def get(self, user_id: UUID) -> UserDetailed:
        return UserDetailed() # Получить из хранилища данные пользователя

    def put(self):
        ...
