from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse

from api import container, schemas
from core.config import settings
from core.logger import logger
from core.tracers import configure_tracer, instrumentor
from managers.user import google_oauth_client

logger()

configure_tracer()

app = FastAPI(
    title=settings.project_name,
    docs_url="/api/v1/openapi",
    openapi_url="/api/v1/openapi.json",
    default_response_class=ORJSONResponse,
)


app.include_router(
    container.api_users.get_register_router(schemas.UserRead, schemas.UserCreate),
    tags=["register"],
)
app.include_router(
    container.api_users.get_auth_router(
        container.access_backend, refresh_backend=container.refresh_backend
    ),
    tags=["auth"],
)
app.include_router(
    container.api_users.get_users_me_router(
        schemas.UserRead, schemas.UserUpdate, schemas.EventRead
    ),
    tags=["users"],
)
app.include_router(
    container.api_users.get_users_router(schemas.UserRead, schemas.UserUpdate),
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
app.include_router(
    container.api_users.get_oauth_router(
        google_oauth_client, container.access_backend, settings.state_secret
    ),
    prefix="/auth/google",
    tags=["auth"],
)


@app.middleware("http")
async def require_request_id(request: Request, call_next):
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        logger().exception('RuntimeError: HEADER X-Request-Id is required')
        raise RuntimeError('RuntimeError: HEADER X-Request-Id is required')
    response = await call_next(request)
    return response


instrumentor().instrument_app(app)  # type: ignore
