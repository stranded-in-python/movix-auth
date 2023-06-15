from typing import AsyncGenerator, List, Optional, Sequence

import httpx
import pytest
from fastapi import Depends, FastAPI, Request, Response, status
from fastapi.security.base import SecurityBase

from api.schemas import U as User
from authentication import AuthenticationBackend, Authenticator
from authentication.authenticator import DuplicateBackendNamesError
from authentication.strategy import Strategy
from authentication.transport import Transport
from core.dependency_types import DependencyCallable
from db import models_protocol as models
from managers.user import BaseUserManager
from openapi import OpenAPIResponseType
from tests.conftest import OAuthAccount, SignInModel, UserModel, UserOAuth

pytestmark = pytest.mark.asyncio


class MockSecurityScheme(SecurityBase):
    def __call__(self, request: Request) -> Optional[str]:
        return "mock"


class MockTransport(Transport):
    scheme: MockSecurityScheme

    def __init__(self):
        self.scheme = MockSecurityScheme()

    async def get_login_response(self, token: str) -> Response:
        ...  # pragma: no cover

    async def get_logout_response(self) -> Response:
        ...  # pragma: no cover

    @staticmethod
    def get_openapi_login_responses_success() -> OpenAPIResponseType:
        """Return a dictionary to use for the openapi responses route parameter."""
        ...  # pragma: no cover

    @staticmethod
    def get_openapi_logout_responses_success() -> OpenAPIResponseType:
        """Return a dictionary to use for the openapi responses route parameter."""
        ...  # pragma: no cover

    def get_scheme(self):
        return self.scheme


class MockStrategy(Strategy[models.UP, models.SIHE]):
    async def read_token(
        self,
        token: str | None,
        user_manager: BaseUserManager[models.UP, models.SIHE, models.OAP, models.UOAP],
    ) -> models.UP | None:
        ...

    async def write_token(self, user: models.UP) -> str:  # pyright: ignore
        ...

    async def destroy_token(self, token: str, user: models.UP) -> None:
        ...


class NoneStrategy(MockStrategy[UserModel, SignInModel]):
    async def read_token(
        self,
        token: Optional[str],
        user_manager: BaseUserManager[UserModel, SignInModel, UserOAuth, OAuthAccount],
    ) -> Optional[UserModel]:
        return None


class UserStrategy(MockStrategy[UserModel, SignInModel]):
    def __init__(self, user: UserModel):
        self.user = user

    async def read_token(
        self,
        token: Optional[str],
        user_manager: BaseUserManager[UserModel, SignInModel, UserOAuth, OAuthAccount],
    ) -> UserModel | None:
        return self.user

    async def write_token(self, user: UserModel) -> str:
        ...

    async def destroy_token(self, token: str, user: UserModel) -> None:
        ...


@pytest.fixture
def get_backend_none():
    def _get_backend_none(name: str = "none"):
        return AuthenticationBackend(
            name=name, transport=MockTransport(), get_strategy=lambda: NoneStrategy()
        )

    return _get_backend_none


@pytest.fixture
def get_backend_user(user: UserModel):
    def _get_backend_user(name: str = "user"):
        return AuthenticationBackend(
            name=name,
            transport=MockTransport(),
            get_strategy=lambda: UserStrategy(user),
        )

    return _get_backend_user


@pytest.fixture
def get_test_auth_client(get_user_manager, get_test_client):
    async def _get_test_auth_client(
        backends: list[AuthenticationBackend[models.UP, models.SIHE]],
        get_enabled_backends: Optional[
            DependencyCallable[Sequence[AuthenticationBackend[models.UP, models.SIHE]]]
        ] = None,
    ) -> AsyncGenerator[httpx.AsyncClient, None]:
        app = FastAPI()
        authenticator = Authenticator(backends, get_user_manager)

        @app.get("/test-current-user", response_model=User)
        def test_current_user(  # pyright: ignore
            user: UserModel = Depends(
                authenticator.current_user(get_enabled_backends=get_enabled_backends)
            ),
        ):
            return user

        @app.get("/test-current-active-user", response_model=User)
        def test_current_active_user(
            user: UserModel = Depends(
                authenticator.current_user(
                    active=True, get_enabled_backends=get_enabled_backends
                )
            )
        ):
            return user

        @app.get("/test-current-superuser", response_model=User)
        def test_current_superuser(
            user: UserModel = Depends(
                authenticator.current_user(
                    active=True,
                    superuser=True,
                    get_enabled_backends=get_enabled_backends,
                )
            )
        ):
            return user

        async for client in get_test_client(app):
            yield client

    return _get_test_auth_client


@pytest.mark.authentication
async def test_authenticator(get_test_auth_client, get_backend_none, get_backend_user):
    async for client in get_test_auth_client([get_backend_none(), get_backend_user()]):
        response = await client.get("/test-current-user")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.authentication
async def test_authenticator_none(get_test_auth_client, get_backend_none):
    async for client in get_test_auth_client(
        [get_backend_none(), get_backend_none(name="none-bis")]
    ):
        response = await client.get("/test-current-user")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.authentication
async def test_authenticator_none_enabled(
    get_test_auth_client, get_backend_none, get_backend_user
):
    backend_none = get_backend_none()
    backend_user = get_backend_user()

    async def get_enabled_backends():
        return [backend_none]

    async for client in get_test_auth_client(
        [backend_none, backend_user], get_enabled_backends
    ):
        response = await client.get("/test-current-user")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.authentication
async def test_authenticators_with_same_name(get_test_auth_client, get_backend_none):
    with pytest.raises(DuplicateBackendNamesError):
        async for _ in get_test_auth_client([get_backend_none(), get_backend_none()]):
            pass
