from typing import Generic, Protocol

from db import models
from managers.user import BaseUserManager


class StrategyDestroyNotSupportedError(Exception):
    pass


class Strategy(Protocol, Generic[models.UP, models.ID]):
    async def read_token(
        self, token: str | None, user_manager: BaseUserManager[models.UP, models.ID]
    ) -> models.UP | None:
        ...

    async def write_token(self, user: models.UP) -> str:
        ...

    async def destroy_token(self, token: str, user: models.UP) -> None:
        ...
