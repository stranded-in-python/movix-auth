from typing import Any, AsyncGenerator, Dict, cast

import httpx
import pytest
from fastapi import FastAPI, status

from api import schemas
from api.auth_users import get_users_me_router, get_users_router
from api.v1.common import ErrorCode
from authentication import Authenticator
from tests.conftest import UserModel, get_mock_authentication

pytestmark = pytest.mark.asyncio


@pytest.fixture
def app_factory(get_user_manager, mock_authentication):
    def _app_factory() -> FastAPI:
        mock_authentication_bis = get_mock_authentication(name="mock-bis")
        authenticator = Authenticator(
            [mock_authentication, mock_authentication_bis], get_user_manager
        )

        user_router = get_users_me_router(
            get_user_manager,
            schemas.UserRead,
            schemas.UserUpdate,
            schemas.EventRead,
            authenticator,
        )

        app = FastAPI()
        app.include_router(user_router)

        app.include_router(
            get_users_router(
                get_user_manager, schemas.UserRead, schemas.UserUpdate, authenticator
            )
        )
        return app

    return _app_factory


@pytest.fixture()
async def test_app_client(
    request, get_test_client, app_factory
) -> AsyncGenerator[httpx.AsyncClient, None]:
    app = app_factory()

    async for client in get_test_client(app):
        yield client


@pytest.mark.router
class TestMe:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        client = test_app_client
        response = await client.get("/api/v1/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_inactive_user(
        self, test_app_client: httpx.AsyncClient, inactive_user: UserModel
    ):
        client = test_app_client
        response = await client.get(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {inactive_user.id}"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_active_user(
        self, test_app_client: httpx.AsyncClient, user: UserModel
    ):
        client = test_app_client
        response = await client.get(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {user.id}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = cast(dict[str, Any], response.json())
        assert data["id"] == str(user.id)
        assert data["email"] == user.email

    async def test_current_user_namespace(self, app_factory):
        assert app_factory().url_path_for("users:current_user") == "/api/v1/users/me"


@pytest.mark.router
class TestUpdateMe:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        client = test_app_client
        response = await client.patch("/api/v1/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_inactive_user(
        self, test_app_client: httpx.AsyncClient, inactive_user: UserModel
    ):
        client = test_app_client
        response = await client.patch(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {inactive_user.id}"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_invalid_password(
        self, test_app_client: httpx.AsyncClient, user: UserModel
    ):
        client = test_app_client
        response = await client.patch(
            "/api/v1/users/me",
            json={"password": "m"},
            headers={"Authorization": f"Bearer {user.id}"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = cast(dict[str, Any], response.json())
        assert data["detail"] == {
            "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
            "reason": "Password should be at least 3 characters",
        }

    async def test_empty_body(
        self, test_app_client: httpx.AsyncClient, user: UserModel
    ):
        client = test_app_client
        response = await client.patch(
            "/api/v1/users/me", json={}, headers={"Authorization": f"Bearer {user.id}"}
        )

        assert response.status_code == status.HTTP_200_OK

        data = cast(dict[str, Any], response.json())
        assert data["email"] == user.email

    async def test_valid_body(
        self, test_app_client: httpx.AsyncClient, user: UserModel
    ):
        client = test_app_client
        json = {"email": "king.arthur@tintagel.bt"}
        response = await client.patch(
            "/api/v1/users/me",
            json=json,
            headers={"Authorization": f"Bearer {user.id}"},
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(dict[str, Any], response.json())
        assert data["email"] == "king.arthur@tintagel.bt"

    async def test_valid_body_is_superuser(
        self, test_app_client: httpx.AsyncClient, user: UserModel
    ):
        client = test_app_client
        json = {"is_superuser": True}
        response = await client.patch(
            "/api/v1/users/me",
            json=json,
            headers={"Authorization": f"Bearer {user.id}"},
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(dict[str, Any], response.json())
        assert data["is_superuser"] is False

    async def test_valid_body_is_active(
        self, test_app_client: httpx.AsyncClient, user: UserModel
    ):
        client = test_app_client
        json = {"is_active": False}
        response = await client.patch(
            "/api/v1/users/me",
            json=json,
            headers={"Authorization": f"Bearer {user.id}"},
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(dict[str, Any], response.json())
        assert data["is_active"] is True

    async def test_valid_body_password(
        self, mocker, mock_user_db, test_app_client: httpx.AsyncClient, user: UserModel
    ):
        client = test_app_client
        mocker.spy(mock_user_db, "update")
        current_hashed_password = user.hashed_password

        json = {"password": "merlin"}
        response = await client.patch(
            "/api/v1/users/me",
            json=json,
            headers={"Authorization": f"Bearer {user.id}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert mock_user_db.update.called is True

        updated_user = mock_user_db.update.call_args[0][0]
        assert updated_user.hashed_password != current_hashed_password


@pytest.mark.router
class TestGetUser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        client = test_app_client
        response = await client.get(
            "/api/v1/users/d35d213e-f3d8-4f08-954a-7e0d1bea286f"
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_regular_user(
        self, test_app_client: httpx.AsyncClient, user: UserModel
    ):
        client = test_app_client
        response = await client.get(
            "/api/v1/users/d35d213e-f3d8-4f08-954a-7e0d1bea286f",
            headers={"Authorization": f"Bearer {user.id}"},
        )
        # TODO Заменить код ассерта
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_not_existing_user_unverified_superuser(
        self, test_app_client: httpx.AsyncClient, superuser: UserModel
    ):
        client = test_app_client
        response = await client.get(
            "/api/v1/users/d35d213e-f3d8-4f08-954a-7e0d1bea286f",
            headers={"Authorization": f"Bearer {superuser.id}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_superuser(
        self, test_app_client: httpx.AsyncClient, user: UserModel, superuser: UserModel
    ):
        client = test_app_client
        response = await client.get(
            f"/api/v1/users/{user.id}",
            headers={"Authorization": f"Bearer {superuser.id}"},
        )

        assert response.status_code == status.HTTP_200_OK

        data = cast(dict[str, Any], response.json())
        assert data["id"] == str(user.id)
        assert "hashed_password" not in data

    async def test_get_user_namespace(self, app_factory, user: UserModel):
        assert (
            app_factory().url_path_for("users:user", id=user.id)
            == f"/api/v1/users/{user.id}"
        )


@pytest.mark.router
class TestUpdateUser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        client = test_app_client
        response = await client.patch(
            "/api/v1/users/d35d213e-f3d8-4f08-954a-7e0d1bea286f"
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_regular_user(
        self, test_app_client: httpx.AsyncClient, user: UserModel
    ):
        client = test_app_client
        response = await client.patch(
            "/api/v1/users/d35d213e-f3d8-4f08-954a-7e0d1bea286f",
            headers={"Authorization": f"Bearer {user.id}"},
        )
        # TODO Заменить код ассерта
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_not_existing_user_unverified_superuser(
        self, test_app_client: httpx.AsyncClient, superuser: UserModel
    ):
        client = test_app_client
        response = await client.patch(
            "/d35d213e-f3d8-4f08-954a-7e0d1bea286f",
            json={},
            headers={"Authorization": f"Bearer {superuser.id}"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_empty_body_unverified_superuser(
        self, test_app_client: httpx.AsyncClient, user: UserModel, superuser: UserModel
    ):
        client = test_app_client
        response = await client.patch(
            f"/api/v1/users/{user.id}",
            json={},
            headers={"Authorization": f"Bearer {superuser.id}"},
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(dict[str, Any], response.json())
        assert data["email"] == user.email

    async def test_valid_body_unverified_superuser(
        self, test_app_client: httpx.AsyncClient, user: UserModel, superuser: UserModel
    ):
        client = test_app_client
        json = {"email": "king.arthur@tintagel.bt"}
        response = await client.patch(
            f"/api/v1/users/{user.id}",
            json=json,
            headers={"Authorization": f"Bearer {superuser.id}"},
        )
        assert response.status_code == status.HTTP_200_OK

        data = cast(dict[str, Any], response.json())
        assert data["email"] == "king.arthur@tintagel.bt"


@pytest.mark.router
class TestDeleteUser:
    async def test_missing_token(self, test_app_client: httpx.AsyncClient):
        client = test_app_client
        response = await client.delete(
            "/api/v1/users/d35d213e-f3d8-4f08-954a-7e0d1bea286f"
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_regular_user(
        self, test_app_client: httpx.AsyncClient, user: UserModel
    ):
        client = test_app_client
        response = await client.delete(
            "/api/v1/users/d35d213e-f3d8-4f08-954a-7e0d1bea286f",
            headers={"Authorization": f"Bearer {user.id}"},
        )
        # TODO заменить ассерт
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_not_existing_user_unverified_superuser(
        self, test_app_client: httpx.AsyncClient, superuser: UserModel
    ):
        client = test_app_client
        response = await client.delete(
            "/api/v1/users/d35d213e-f3d8-4f08-954a-7e0d1bea286f",
            headers={"Authorization": f"Bearer {superuser.id}"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_unverified_superuser(
        self,
        mocker,
        mock_user_db,
        test_app_client: httpx.AsyncClient,
        user: UserModel,
        superuser: UserModel,
    ):
        client = test_app_client
        mocker.spy(mock_user_db, "delete")

        response = await client.delete(
            f"/api/v1/users/{user.id}",
            headers={"Authorization": f"Bearer {superuser.id}"},
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.content == b""
        assert mock_user_db.delete.called is True

        deleted_user = mock_user_db.delete.call_args[0][0]
        assert deleted_user.id == user.id
