import httpx
import pytest
from fastapi import FastAPI, status

from api import schemas
from api.container import APIUsers as FastAPIUsers
from tests.conftest import SignInModel, UserModel


@pytest.fixture
def fastapi_users(get_user_manager, mock_authentication) -> FastAPIUsers:
    return FastAPIUsers[UserModel, SignInModel](
        get_user_manager,
        [mock_authentication],
        [mock_authentication],
        schemas.UCH,
        schemas.CH,
    )


@pytest.fixture
def test_app(fastapi_users: FastAPIUsers, mock_authentication) -> FastAPI:
    app = FastAPI()
    app.include_router(fastapi_users.return_register_router(schemas.U, schemas.UC))
    app.include_router(fastapi_users.return_reset_password_router())
    app.include_router(
        fastapi_users.return_auth_router(mock_authentication, mock_authentication)
    )
    app.include_router(
        fastapi_users.return_users_me_router(schemas.U, schemas.UU, schemas.EventRead)
    )
    app.include_router(fastapi_users.return_users_router(schemas.U, schemas.UU))

    return app


@pytest.fixture
async def test_app_client(test_app, get_test_client):
    async for client in get_test_client(test_app):
        yield client


@pytest.fixture
def openapi_dict(test_app: FastAPI):
    return test_app.openapi()


@pytest.fixture
def url_prefix():
    return "/api/v1"


@pytest.mark.openapi
async def test_openapi_route(test_app_client: httpx.AsyncClient, url_prefix: str):
    response = await test_app_client.get("/openapi.json")
    assert response.status_code == status.HTTP_200_OK


class TestReset:
    def test_reset_password_status_codes(self, openapi_dict, url_prefix):
        route = openapi_dict["paths"][url_prefix + "/reset-password"]["post"]
        assert list(route["responses"].keys()) == ["200", "400", "422"]

    def test_forgot_password_status_codes(self, openapi_dict, url_prefix):
        route = openapi_dict["paths"][url_prefix + "/forgot-password"]["post"]
        assert list(route["responses"].keys()) == ["202", "422"]


class TestUsers:
    def test_patch_id_status_codes(self, openapi_dict, url_prefix):
        route = openapi_dict["paths"][url_prefix + "/users/{id}"]["patch"]
        assert list(route["responses"].keys()) == [
            "200",
            "401",
            "403",
            "404",
            "400",
            "422",
        ]

    def test_delete_id_status_codes(self, openapi_dict, url_prefix):
        route = openapi_dict["paths"][url_prefix + "/users/{id}"]["delete"]
        assert list(route["responses"].keys()) == ["204", "401", "403", "404", "422"]

    def test_get_id_status_codes(self, openapi_dict, url_prefix):
        route = openapi_dict["paths"][url_prefix + "/users/{id}"]["get"]
        assert list(route["responses"].keys()) == ["200", "401", "403", "404", "422"]

    def test_patch_me_status_codes(self, openapi_dict, url_prefix):
        route = openapi_dict["paths"][url_prefix + "/users/me"]["patch"]
        assert list(route["responses"].keys()) == ["200", "401", "400", "422"]

    def test_get_me_status_codes(self, openapi_dict, url_prefix):
        route = openapi_dict["paths"][url_prefix + "/users/me"]["get"]
        assert list(route["responses"].keys()) == ["200", "401"]


class TestRegister:
    def test_register_status_codes(self, openapi_dict, url_prefix):
        route = openapi_dict["paths"][url_prefix + "/register"]["post"]
        assert list(route["responses"].keys()) == ["201", "400", "422"]
