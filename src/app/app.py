from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import auth, roles, register
from authentication import Authenticator, AuthenticationBackend, JWTStrategy, BearerTransport
from core.config import settings

from app.users import api_users
from app.roles import api_roles
from app.access_rights import api_access_rights
from app.schemas import UserCreate, UserRead, UserUpdate

app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

app.include_router(
    api_users.get_register_router(UserRead, UserCreate),
    tags=["register"]
)
app.include_router(
    api_users.get_auth_router(),
    tags=["auth"]
)
app.include_router(
    api_users.get_users_router(UserRead, UserUpdate),
    tags=["users"],
)
app.include_router(
    api_roles.get_roles_router,
    tags=["roles"]
)
app.include_router(
    api_access_rights.get_access_rights_router(),
    tags=["access rights"]
)

@app.on_event("startup")
async def startup():
    ...


@app.on_event("shutdown")
async def shutdown():
    ...
