from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

import app.schemas as a_sch
from app.services.access_rights import api_access_rights
from app.services.auth import auth_backend
from app.services.roles import api_roles
from app.services.users import api_users
from core.config import settings

app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

app.include_router(
    api_users.get_register_router(a_sch.UserRead, a_sch.UserCreate), tags=["register"]
)
app.include_router(api_users.get_auth_router(auth_backend), tags=["auth"])
app.include_router(
    api_users.get_users_router(a_sch.UserRead, a_sch.UserUpdate, a_sch.EventRead),
    tags=["users"],
)
app.include_router(
    api_roles.get_roles_router(
        a_sch.RoleRead,
        a_sch.RoleCreate,
        a_sch.RoleUpdate,
        a_sch.UserRoleRead,
        a_sch.UserRoleUpdate,
    ),
    tags=["roles"],
)
# app.include_router(
#     api_access_rights.get_access_rights_router(),
#     tags=["access rights"]
# )


@app.on_event("startup")
async def on_startup():
    ...


@app.on_event("shutdown")
async def shutdown():
    ...
