import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from services.user import get_user_service
from api.v1 import auth, roles, user, register
from authentication import Authenticator, AuthenticationBackend, JWTStrategy, BearerTransport
from core.config import settings
from schemas import BaseUser, BaseUserUpdate

app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

@app.on_event("startup")
async def startup():
    ...


@app.on_event("shutdown")
async def shutdown():
    ...


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


SECRET = "SECRET"
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
auth_service = Authenticator([auth_backend], get_user_service())

app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(roles.router, prefix="/api/v1", tags=["roles"])
app.include_router(
    user.get_users_router(
        get_user_service=get_user_service,
        authenticator=auth_service
    ),
    prefix="/api/v1",
    tags=["user"]
)
app.include_router(register.router, prefix="/api/v1", tags=["register"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=['/app']
    )
