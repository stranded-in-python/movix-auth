from abc import ABC, abstractmethod
from uuid import UUID

import src.models.models as m


class BaseUserService(ABC):
    @abstractmethod
    async def register(
            self,
            params: m.UserRegistrationParamsIn
    ) -> m.UserRegistrationParamsOut:
        ...

    @abstractmethod
    def get(self, user_id: UUID) -> m.UserDetailed:
        ...

    @abstractmethod
    def change_password(self, params: m.UserUpdateIn) -> m.UserUpdateOut:
        ...


class BaseAuthService(ABC):
    @abstractmethod
    async def login(self, params: m.LoginParamsIn) -> m.LoginParamsOut:
        ...

    @abstractmethod
    async def logout(self, params: m.UserPayload) -> None:
        ...


class BaseRoleService(ABC):
    ...
