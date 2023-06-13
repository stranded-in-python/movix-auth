from typing import Any, AsyncGenerator, Dict, cast

import httpx
import pytest
from fastapi import FastAPI, status

from api import schemas
from api.auth_users import get_register_router
from api.v1.common import ErrorCode


@pytest.fixture
@pytest.mark.asyncio
async def test_app_client(
    get_user_manager, get_test_client
) -> AsyncGenerator[httpx.AsyncClient, None]:
    register_router = get_register_router(
        get_user_manager, schemas.UserRead, schemas.UserCreate
    )

    app = FastAPI()
    app.include_router(register_router)

    async for client in get_test_client(app):
        yield client


@pytest.mark.router
@pytest.mark.asyncio
class TestRegister:
    async def test_empty_body(self, test_app_client: httpx.AsyncClient):
        response = await test_app_client.post("/api/v1/register", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_missing_email(self, test_app_client: httpx.AsyncClient):
        json = {"password": "guinevere"}
        response = await test_app_client.post("/api/v1/register", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_missing_password(self, test_app_client: httpx.AsyncClient):
        json = {"email": "king.arthur@camelot.bt"}
        response = await test_app_client.post("/api/v1/register", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_wrong_email(self, test_app_client: httpx.AsyncClient):
        json = {"email": "king.arthur", "password": "guinevere"}
        response = await test_app_client.post("/api/v1/register", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_invalid_password(self, test_app_client: httpx.AsyncClient):
        json = {"email": "king.arthur@camelot.bt", "password": "g"}
        response = await test_app_client.post("/api/v1/register", json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == {
            "code": ErrorCode.REGISTER_INVALID_PASSWORD,
            "reason": "Password should be at least 3 characters",
        }

    @pytest.mark.parametrize(
        "email, username",
        [
            ["king.arthur@camelot.bt", "king.arthur"],
            ["King.Arthur@camelot.bt", "king.arthur"],
        ],
    )
    async def test_existing_user(
        self, email, username, test_app_client: httpx.AsyncClient
    ):
        json = {"email": email, "username": username, "password": "guinevere"}
        response = await test_app_client.post("/api/v1/register", json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(Dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.REGISTER_USER_ALREADY_EXISTS

    @pytest.mark.parametrize(
        "email,username",
        [["lancelot@camelot.bt", "lancelot"], ["Lancelot@camelot.bt", "lancelot"]],
    )
    async def test_valid_body(
        self, email, username, test_app_client: httpx.AsyncClient
    ):
        json = {"email": email, "username": username, "password": "guinevere"}
        response = await test_app_client.post("/api/v1/register", json=json)
        assert response.status_code == status.HTTP_201_CREATED

        data = cast(Dict[str, Any], response.json())
        assert "hashed_password" not in data
        assert "password" not in data
        assert data["id"] is not None

    async def test_valid_body_is_superuser(self, test_app_client: httpx.AsyncClient):
        json = {
            "email": "lancelot@camelot.bt",
            "username": "lancelot",
            "password": "guinevere",
            "is_superuser": True,
        }
        response = await test_app_client.post("/api/v1/register", json=json)
        assert response.status_code == status.HTTP_201_CREATED

        data = cast(Dict[str, Any], response.json())
        assert data["is_superuser"] is False

    async def test_valid_body_is_active(self, test_app_client: httpx.AsyncClient):
        json = {
            "email": "lancelot@camelot.bt",
            "username": "lancelot",
            "password": "guinevere",
            "is_active": False,
        }
        response = await test_app_client.post("/api/v1/register", json=json)
        assert response.status_code == status.HTTP_201_CREATED

        data = cast(Dict[str, Any], response.json())
        assert data["is_active"] is True


@pytest.mark.asyncio
async def test_register_namespace(get_user_manager):
    app = FastAPI()
    app.include_router(get_register_router(get_user_manager, schemas.U, schemas.UC))
    assert app.url_path_for("register") == "/api/v1/register"
