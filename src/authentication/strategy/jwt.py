import logging
from typing import Generic

import jwt

import core.exceptions as exceptions
from authentication.strategy.base import Strategy, StrategyDestroyNotSupportedError
from authentication.strategy.blacklist import TokenBlacklistManager
from core.jwt_utils import SecretType, decode_jwt, generate_jwt
from db import models_protocol
from managers.user import BaseUserManager


class JWTStrategy(
    Strategy[models_protocol.UP, models_protocol.SIHE],
    Generic[models_protocol.UP, models_protocol.SIHE],
):
    def __init__(
        self,
        secret: SecretType,
        lifetime_seconds: int | None,
        token_audience: list[str] = ["fastapi-users:auth"],
        algorithm: str = "HS256",
        public_key: SecretType | None = None,
    ):
        self.secret = secret
        self.lifetime_seconds = lifetime_seconds
        self.token_audience = token_audience
        self.algorithm = algorithm
        self.public_key = public_key

    @property
    def encode_key(self) -> SecretType:
        return self.secret

    @property
    def decode_key(self) -> SecretType:
        return self.public_key or self.secret

    async def read_token(
        self,
        token: str | None,
        user_manager: BaseUserManager[
            models_protocol.UP,
            models_protocol.SIHE,
            models_protocol.OAP,
            models_protocol.UOAP,
        ],
    ) -> models_protocol.UP | None:
        if token is None:
            return None

        try:
            data = decode_jwt(
                token, self.decode_key, self.token_audience, algorithms=[self.algorithm]
            )
            user_id = data.get("sub")
            if user_id is None:
                return None
        except jwt.PyJWTError as e:
            logging.warning(e)
            return None

        try:
            parsed_id = user_manager.parse_id(user_id)
            return await user_manager.get(parsed_id)
        except (exceptions.UserNotExists, exceptions.InvalidID):
            return None

    async def write_token(self, user: models_protocol.UP) -> str:
        data = {"sub": str(user.id), "aud": self.token_audience}
        return generate_jwt(
            data, self.encode_key, self.lifetime_seconds, algorithm=self.algorithm
        )

    async def destroy_token(self, token: str, user: models_protocol.UP) -> None:
        raise StrategyDestroyNotSupportedError(
            "A JWT can't be invalidated: it's valid until it expires."
        )


class JWTBlacklistStrategy(
    JWTStrategy[models_protocol.UP, models_protocol.SIHE],
    Generic[models_protocol.UP, models_protocol.SIHE],
):
    def __init__(
        self,
        secret: SecretType,
        lifetime_seconds: int | None,
        token_audience: list[str] = ["fastapi-users:auth"],
        algorithm: str = "HS256",
        public_key: SecretType | None = None,
        blacklist_manager: TokenBlacklistManager | None = None,
    ):
        self.blacklist_manager = blacklist_manager
        super().__init__(
            secret, lifetime_seconds, token_audience, algorithm, public_key
        )

    async def read_token(
        self,
        token: str | None,
        user_manager: BaseUserManager[
            models_protocol.UP,
            models_protocol.SIHE,
            models_protocol.OAP,
            models_protocol.UOAP,
        ],
    ) -> models_protocol.UP | None:
        if self.blacklist_manager and await self.blacklist_manager.check_token(token):
            return None
        return await super().read_token(token, user_manager)

    async def destroy_token(self, token: str, user: models_protocol.UP) -> None:
        if self.blacklist_manager:
            await self.blacklist_manager.enlist(token)
        return await super().destroy_token(token, user)
