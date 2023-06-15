from typing import Any, AsyncGenerator, Dict, Tuple, cast

import httpx
import pytest
from fastapi import FastAPI, status

from api.auth_users import get_auth_router
from api.v1.common import ErrorCode
from authentication import Authenticator
from tests.conftest import UserModel, get_mock_authentication, get_user_manager

pytestmark = pytest.mark.asyncio


@pytest.fixture
def app_factory(get_user_manager, mock_authentication):
    def _app_factory(requires_verification: bool) -> FastAPI:
        mock_authentication_bis = get_mock_authentication(name="mock-bis")
        authenticator = Authenticator(
            [mock_authentication, mock_authentication_bis], get_user_manager
        )

        mock_auth_router = get_auth_router(
            mock_authentication,
            mock_authentication,
            get_user_manager,
            authenticator,
            authenticator,
            requires_verification=requires_verification,
        )
        mock_bis_auth_router = get_auth_router(
            mock_authentication_bis,
            mock_authentication_bis,
            get_user_manager,
            authenticator,
            authenticator,
            requires_verification=requires_verification,
        )

        app = FastAPI()
        app.include_router(mock_auth_router, prefix="/mock")
        app.include_router(mock_bis_auth_router, prefix="/mock-bis")

        return app

    return _app_factory


@pytest.fixture(
    params=[True, False], ids=["required_verification", "not_required_verification"]
)
async def test_app_client(
    request, get_test_client, app_factory
) -> AsyncGenerator[tuple[httpx.AsyncClient, bool], None]:
    requires_verification = request.param
    app = app_factory(requires_verification)

    async for client in get_test_client(app):
        yield client, requires_verification


@pytest.mark.router
@pytest.mark.parametrize("path", ["/mock/api/v1/login", "/mock-bis/api/v1/login"])
class TestLogin:
    async def test_empty_body(
        self, path, test_app_client: tuple[httpx.AsyncClient, bool], user_manager
    ):
        client, _ = test_app_client
        response = await client.post(path, data={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert user_manager.on_after_login.called is False

    async def test_missing_username(
        self, path, test_app_client: tuple[httpx.AsyncClient, bool], user_manager
    ):
        client, _ = test_app_client
        data = {"password": "guinevere"}
        response = await client.post(path, data=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert user_manager.on_after_login.called is False

    async def test_missing_password(
        self, path, test_app_client: tuple[httpx.AsyncClient, bool], user_manager
    ):
        client, _ = test_app_client
        data = {"username": "king.arthur@camelot.bt"}
        response = await client.post(path, data=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert user_manager.on_after_login.called is False

    async def test_not_existing_user(
        self, path, test_app_client: tuple[httpx.AsyncClient, bool], user_manager
    ):
        client, _ = test_app_client
        data = {"username": "lancelot@camelot.bt", "password": "guinevere"}
        response = await client.post(path, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.LOGIN_BAD_CREDENTIALS
        assert user_manager.on_after_login.called is False

    async def test_wrong_password(
        self, path, test_app_client: tuple[httpx.AsyncClient, bool], user_manager
    ):
        client, _ = test_app_client
        data = {"username": "king.arthur@camelot.bt", "password": "percival"}
        response = await client.post(path, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(dict[str, Any], response.json())
        assert data["detail"] == ErrorCode.LOGIN_BAD_CREDENTIALS
        assert user_manager.on_after_login.called is False

    @pytest.mark.parametrize(
        "username, status_code",
        [["king.arthur", status.HTTP_200_OK], ["foo", status.HTTP_400_BAD_REQUEST]],
    )
    async def test_valid_credentials(
        self,
        path,
        username,
        status_code,
        test_app_client: tuple[httpx.AsyncClient, bool],
        user_manager,
        user: UserModel,
    ):
        client, _ = test_app_client
        data = {"username": username, "password": "guinevere"}
        response = await client.post(path, data=data)
        assert response.status_code == status_code
        if status_code == status.HTTP_400_BAD_REQUEST:
            data = cast(dict[str, Any], response.json())
            assert data["detail"] == ErrorCode.LOGIN_BAD_CREDENTIALS
            assert user_manager.on_after_login.called is False
        else:
            assert response.json() == {
                "access_token": str(user.id),
                "token_type": "bearer",
            }
            assert user_manager.on_after_login.called is True


@pytest.mark.router
@pytest.mark.parametrize("path", ["/mock/api/v1/logout", "/mock-bis/api/v1/logout"])
class TestLogout:
    async def test_missing_token(
        self, path, test_app_client: tuple[httpx.AsyncClient, bool]
    ):
        client, _ = test_app_client
        response = await client.post(path)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_valid_credentials(
        self,
        mocker,
        path,
        test_app_client: tuple[httpx.AsyncClient, bool],
        user: UserModel,
    ):
        client, requires_verification = test_app_client
        response = await client.post(
            path, headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.router
async def test_route_names(app_factory, mock_authentication):
    app = app_factory(False)
    login_route_name = f"auth:{mock_authentication.name}.login"
    assert app.url_path_for(login_route_name) == "/mock/api/v1/login"

    logout_route_name = f"auth:{mock_authentication.name}.logout"
    assert app.url_path_for(logout_route_name) == "/mock/api/v1/logout"
