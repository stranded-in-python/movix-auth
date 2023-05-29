from authentication.strategy.base import Strategy, StrategyDestroyNotSupportedError
from authentication.strategy.db import (
    AP,
    AccessTokenDatabase,
    AccessTokenProtocol,
    DatabaseStrategy,
)
from authentication.strategy.jwt import JWTStrategy

try:
    from fastapi_users.authentication.strategy.redis import RedisStrategy
except ImportError:  # pragma: no cover
    pass

__all__ = [
    "AP",
    "AccessTokenDatabase",
    "AccessTokenProtocol",
    "DatabaseStrategy",
    "JWTStrategy",
    "Strategy",
    "StrategyDestroyNotSupportedError",
    "RedisStrategy",
]
