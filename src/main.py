import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import auth, roles, user
from core.config import settings


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


app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(roles.router, prefix="/api/v1", tags=["roles"])
app.include_router(user.router, prefix="/api/v1", tags=["persons"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=['/app']
    )
