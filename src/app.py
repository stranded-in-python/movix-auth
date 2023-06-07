from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api import container
from api import schemas
from core.config import settings

app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

app.include_router(
    container.api_users.get_register_router(schemas.UserRead, schemas.UserCreate),
    tags=["register"],
)
app.include_router(
    container.api_users.get_auth_router(container.auth_backend), tags=["auth"]
)
app.include_router(
    container.api_users.get_users_me_router(
        schemas.UserRead,
        schemas.UserUpdate,
        schemas.EventRead,
    ),
    tags=["users"],
)
app.include_router(
    container.api_users.get_users_router(
        schemas.UserRead,
        schemas.UserUpdate,
    ),
    tags=["users"],
)
app.include_router(
    container.api_roles.get_roles_router(
        schemas.RoleRead,
        schemas.RoleCreate,
        schemas.RoleUpdate,
        schemas.UserRoleRead,
        schemas.UserRoleUpdate,
    ),
    tags=["roles"],
)
app.include_router(
    container.api_access_rights.get_access_rights_router(
        schemas.AccessRightRead,
        schemas.AccessRightCreate,
        schemas.AccessRightUpdate,
        schemas.RoleAccessRightRead,
        schemas.RoleAccessRightUpdate,
    ),
    tags=["access rights"],
)


@app.on_event("startup")
async def on_startup():
    ...


@app.on_event("shutdown")
async def shutdown():
    ...
