from typing import Generic, Protocol

from db import models_protocol
from managers.user import BaseUserManager


class StrategyDestroyNotSupportedError(Exception):
    pass


class Strategy(Protocol[models_protocol.UP, models_protocol.SIHE]):
    async def read_token(
        self,
        token: str | None,
        user_manager: BaseUserManager[models_protocol.UP, models_protocol.SIHE],
    ) -> models_protocol.UP | None:
        ...

    async def write_token(self, user: models_protocol.UP) -> str:
        ...

    async def destroy_token(self, token: str, user: models_protocol.UP) -> None:
        ...
