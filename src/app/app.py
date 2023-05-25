from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import auth, roles, register
from authentication import Authenticator, AuthenticationBackend, JWTStrategy, BearerTransport
from core.config import settings

from app.users import api_users
from app.schemas import UserCreate, UserRead, UserUpdate

app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

app.include_router(
    api_users.get_auth_router(),
    tags=["auth"]
)
app.include_router(
    roles.router,
    tags=["roles"]
)
app.include_router(
    api_users.get_users_router(UserRead, UserUpdate),
    tags=["users"],
)
app.include_router(
    api_users.get_register_router(UserRead, UserCreate),
    tags=["register"]
)


@app.on_event("startup")
async def startup():
    ...


@app.on_event("shutdown")
async def shutdown():
    ...
