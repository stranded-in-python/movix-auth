from abc import ABC, abstractmethod
from uuid import UUID

import src.models.models as m

class BaseUserService(ABC):
    @abstractmethod
    def get(self, user_id: UUID) -> m.UserDetailed:
        ...

    @abstractmethod
    def put(self, params: m.UserUpdateIn) -> m.UserUpdateOut:
        ...


class BaseAuthService(ABC):
    @abstractmethod
    def register(self, params: m.UserRegistrationParamsIn) -> None:
        ...
    @abstractmethod
    def login(self, params: m.LoginParamsIn) -> m.LoginParamsOut:
        ...

    @abstractmethod
    def logout(self, params: m.UserPayload) -> None:
        ...


class BaseRoleService(ABC):
    ...
