from typing import AsyncGenerator, Optional

import httpx
import pytest
from fastapi import Depends, FastAPI, status

from api import schemas
from api.container import APIUsers as FastAPIUsers
from db.schemas import models
from tests.conftest import UserModel


@pytest.fixture
@pytest.mark.asyncio
async def test_app_client(
    secret, get_user_manager, mock_authentication, get_test_client
) -> AsyncGenerator[httpx.AsyncClient, None]:
    fastapi_users = FastAPIUsers[models.UserRead, models.SIHE](
        get_user_manager, [mock_authentication], [mock_authentication]
    )

    app = FastAPI()
    app.include_router(fastapi_users.get_register_router(schemas.UserRead, schemas.UserCreate))
    app.include_router(fastapi_users.get_reset_password_router())
    app.include_router(
        fastapi_users.get_auth_router(mock_authentication, mock_authentication)
    )

    @app.delete("/users/me")
    def custom_users_route():
        return None

    app.include_router(
        fastapi_users.get_users_router(schemas.UserRead, schemas.UserUpdate)
    )

    @app.get("/current-user", response_model=schemas.UserRead)
    def current_user(user: UserModel = Depends(fastapi_users.current_user())):
        return user

    @app.get("/current-active-user", response_model=schemas.UserRead)
    def current_active_user(
        user: UserModel = Depends(fastapi_users.current_user(active=True)),
    ):
        return user

    @app.get("/current-superuser", response_model=schemas.UserRead)
    def current_superuser(
        user: UserModel = Depends(
            fastapi_users.current_user(active=True, superuser=True)
        )
    ):
        return user

    @app.get("/optional-current-user")
    def optional_current_user(
        user: Optional[UserModel] = Depends(fastapi_users.current_user(optional=True)),
    ):
        return schemas.UserRead.from_orm(user) if user else None

    @app.get("/optional-current-active-user")
    def optional_current_active_user(
        user: Optional[UserModel] = Depends(
            fastapi_users.current_user(optional=True, active=True)
        )
    ):
        return schemas.UserRead.from_orm(user) if user else None

    @app.get("/optional-current-superuser")
    def optional_current_superuser(
        user: Optional[UserModel] = Depends(
            fastapi_users.current_user(optional=True, active=True, superuser=True)
        )
    ):
        return schemas.UserRead.from_orm(user) if user else None

    async for client in get_test_client(app):
        yield client


@pytest.mark.fastapi_users
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path,method",
    [
        ("api/v1/register", "POST"),
        ("api/v1/forgot-password", "POST"),
        ("api/v1/reset-password", "POST"),
        ("api/v1/login", "POST"),
        ("api/v1/logout", "POST"),
        ("api/v1/register", "POST"),
        ("api/v1/users/d35d213e-f3d8-4f08-954a-7e0d1bea286f", "GET"),
        ("api/v1/users/d35d213e-f3d8-4f08-954a-7e0d1bea286f", "PATCH"),
        ("api/v1/users/d35d213e-f3d8-4f08-954a-7e0d1bea286f", "DELETE"),
    ],
)
async def test_route_exists(test_app_client: httpx.AsyncClient, path: str, method: str):
    response = await test_app_client.request(method, path)
    assert response.status_code not in (
        status.HTTP_404_NOT_FOUND,
        status.HTTP_405_METHOD_NOT_ALLOWED,
    )


@pytest.mark.fastapi_users
@pytest.mark.asyncio
async def test_custom_users_route_not_catched(test_app_client: httpx.AsyncClient):
    response = await test_app_client.request("DELETE", "/users/me")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.fastapi_users
@pytest.mark.asyncio
class TestGetCurrentUser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get("/current-user")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_invalid_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get(
            "/current-user", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_valid_token(
        self, test_app_client: httpx.AsyncClient, user: UserModel
    ):
        response = await test_app_client.get(
            "/current-user", headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.fastapi_users
@pytest.mark.asyncio
class TestGetCurrentActiveUser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get("/current-active-user")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_invalid_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get(
            "/current-active-user", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_valid_token_inactive_user(
        self, test_app_client: httpx.AsyncClient, inactive_user: UserModel
    ):
        response = await test_app_client.get(
            "/current-active-user",
            headers={"Authorization": f"Bearer {inactive_user.id}"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_valid_token(
        self, test_app_client: httpx.AsyncClient, user: UserModel
    ):
        response = await test_app_client.get(
            "/current-active-user", headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.fastapi_users
@pytest.mark.asyncio
class TestGetCurrentSuperuser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get("/current-superuser")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_invalid_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get(
            "/current-superuser", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_valid_token_regular_user(
        self, test_app_client: httpx.AsyncClient, user: UserModel
    ):
        response = await test_app_client.get(
            "/current-superuser", headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_valid_token_superuser(
        self, test_app_client: httpx.AsyncClient, superuser: UserModel
    ):
        response = await test_app_client.get(
            "/current-superuser", headers={"Authorization": f"Bearer {superuser.id}"}
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.fastapi_users
@pytest.mark.asyncio
class TestOptionalGetCurrentUser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get("/optional-current-user")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_invalid_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get(
            "/optional-current-user", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_valid_token(
        self, test_app_client: httpx.AsyncClient, user: UserModel
    ):
        response = await test_app_client.get(
            "/optional-current-user", headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is not None


@pytest.mark.fastapi_users
@pytest.mark.asyncio
class TestOptionalGetCurrentActiveUser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get("/optional-current-active-user")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_invalid_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get(
            "/optional-current-active-user", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_valid_token_inactive_user(
        self, test_app_client: httpx.AsyncClient, inactive_user: UserModel
    ):
        response = await test_app_client.get(
            "/optional-current-active-user",
            headers={"Authorization": f"Bearer {inactive_user.id}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_valid_token(
        self, test_app_client: httpx.AsyncClient, user: UserModel
    ):
        response = await test_app_client.get(
            "/optional-current-active-user",
            headers={"Authorization": f"Bearer {user.id}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is not None


@pytest.mark.fastapi_users
@pytest.mark.asyncio
class TestOptionalGetCurrentSuperuser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get("/optional-current-superuser")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_invalid_token(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.get(
            "/optional-current-superuser", headers={"Authorization": "Bearer foo"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_valid_token_regular_user(
        self, test_app_client: httpx.AsyncClient, user: UserModel
    ):
        response = await test_app_client.get(
            "/optional-current-superuser",
            headers={"Authorization": f"Bearer {user.id}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_valid_token_superuser(
        self, test_app_client: httpx.AsyncClient, superuser: UserModel
    ):
        response = await test_app_client.get(
            "/optional-current-superuser",
            headers={"Authorization": f"Bearer {superuser.id}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is not None
