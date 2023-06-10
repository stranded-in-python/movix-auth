from authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTBlacklistStrategy,
    RefreshBearerTransport,
    get_manager,
)
from core.config import settings
from db.schemas import models

bearer_transport = BearerTransport(token_url="auth/jwt/login")
refresh_bearer_transport = RefreshBearerTransport(token_url="auth/jwt/refresh")


def get_refresh_strategy() -> JWTBlacklistStrategy[models.UserRead, models.EventRead]:
    return JWTBlacklistStrategy(
        secret=settings.refresh_token_secret,
        lifetime_seconds=3599,
        blacklist_manager=get_manager('jwt_refresh'),
    )


def get_access_strategy() -> JWTBlacklistStrategy[models.UserRead, models.EventRead]:
    return JWTBlacklistStrategy(
        secret=settings.access_token_secret,
        lifetime_seconds=119,
        blacklist_manager=get_manager('jwt_access'),
    )


refresh_backend = AuthenticationBackend[models.UserRead, models.EventRead](
    name="jwt_refresh",
    transport=refresh_bearer_transport,
    get_strategy=get_refresh_strategy,
)


access_backend = AuthenticationBackend[models.UserRead, models.EventRead](
    name="jwt_access", transport=bearer_transport, get_strategy=get_access_strategy
)
