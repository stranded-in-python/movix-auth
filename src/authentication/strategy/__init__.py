from authentication.strategy.base import Strategy, StrategyDestroyNotSupportedError
from authentication.strategy.db import (
    AP,
    AccessTokenProtocol,
    DatabaseStrategy,
    TokenBlacklistManager,
)
from authentication.strategy.jwt import JWTStrategy

try:
    from fastapi_users.authentication.strategy.redis import RedisStrategy
except ImportError:  # pragma: no cover
    pass

__all__ = [
    "AP",
    "TokenBlacklistManager",
    "AccessTokenProtocol",
    "DatabaseStrategy",
    "JWTStrategy",
    "Strategy",
    "StrategyDestroyNotSupportedError",
    "RedisStrategy",
]
