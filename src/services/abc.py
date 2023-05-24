from abc import ABC, abstractmethod
from uuid import UUID

from fastapi import Request, Response

import models as m
import schemas as schemas


class BaseUserService(ABC):
    @abstractmethod
    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Request | None = None
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
