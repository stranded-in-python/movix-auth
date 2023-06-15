from typing import Protocol

from db import models_protocol
from managers.user import BaseUserManager


class StrategyDestroyNotSupportedError(Exception):
    pass


class Strategy(Protocol[models_protocol.UP, models_protocol.SIHE]):
    async def read_token(
        self,
        token: str | None,
        user_manager: BaseUserManager[models_protocol.UP, models_protocol.SIHE, models_protocol.OAP, models_protocol.UOAP],
    ) -> models_protocol.UP | None:
        ...

    async def write_token(self, user: models_protocol.UP) -> str:
        ...

    async def destroy_token(self, token: str, user: models_protocol.UP) -> None:
        ...


class TokenBlacklistStorage(Protocol):
    async def add_to_set(self, set_name: str, value: str):
        ...

    async def is_in_set(self, set_name: str, value: str) -> bool:
        ...

    async def destroy_set(self, set_name: str):
        ...

    async def remove_from_set(self, set_name: str, value: str):
        ...
