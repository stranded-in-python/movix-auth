from authentication.authenticator import Authenticator
from authentication.backend import AuthenticationBackend
from authentication.strategy import JWTStrategy, Strategy

try:
    from fastapi_users.authentication.strategy import RedisStrategy
except ImportError:  # pragma: no cover
    pass

from authentication.transport import (
    BearerTransport,
    CookieTransport,
    Transport,
)

__all__ = [
    "Authenticator",
    "AuthenticationBackend",
    "BearerTransport",
    "CookieTransport",
    "JWTStrategy",
    "RedisStrategy",
    "Strategy",
    "Transport",
]
