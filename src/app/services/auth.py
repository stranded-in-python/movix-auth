from authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from core.config import settings

bearer_transport = BearerTransport(token_url="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.verification_token_secret, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt", transport=bearer_transport, get_strategy=get_jwt_strategy
)
