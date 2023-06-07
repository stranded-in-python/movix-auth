import secrets
from typing import Generic, Optional, TypeVar

import redis.asyncio

import core.exceptions as exceptions
from authentication.strategy.base import Strategy
import db.models_protocol as models
from managers.user import BaseUserManager


class RedisStrategy(
    Strategy[models.UP, models.SIHE],
    Generic[models.UP, models.SIHE, TypeVar("Redis")],
):
    def __init__(
        self,
        redis: redis.asyncio.Redis[str],  # ignore type
        lifetime_seconds: Optional[int] = None,
        *,
        key_prefix: str = "fastapi_users_token:",
    ):
        self.redis = redis
        self.lifetime_seconds = lifetime_seconds
        self.key_prefix = key_prefix

    async def read_token(
        self,
        token: Optional[str],
        user_manager: BaseUserManager[models.UP, models.SIHE],
    ) -> Optional[models.UP]:
        if token is None:
            return None

        user_id = self.redis.get(f"{self.key_prefix}{token}")
        if user_id is None:
            return None

        try:
            parsed_id = user_manager.parse_id(user_id)
            return await user_manager.get(parsed_id)
        except (exceptions.UserNotExists, exceptions.InvalidID):
            return None

    async def write_token(self, user: models.UP) -> str:
        token = secrets.token_urlsafe()
        self.redis.set(
            f"{self.key_prefix}{token}", str(user.id), ex=self.lifetime_seconds
        )
        return token

    async def destroy_token(self, token: str, user: models.UP) -> None:
        self.redis.delete(f"{self.key_prefix}{token}")
