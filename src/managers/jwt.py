from authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from core.config import settings
from db.schemas import models

bearer_transport = BearerTransport(token_url="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy[models.UserRead, models.EventRead]:
    return JWTStrategy(
        secret=settings.verification_password_token_secret, lifetime_seconds=3599
    )


auth_backend = AuthenticationBackend[models.UserRead, models.EventRead](
    name="jwt", transport=bearer_transport, get_strategy=get_jwt_strategy
)
