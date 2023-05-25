from authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

SECRET = "SECRET"
bearer_transport = BearerTransport(token_url="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)