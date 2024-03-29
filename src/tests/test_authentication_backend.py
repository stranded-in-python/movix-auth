from typing import Callable, Generic, Optional, Type, cast

import pytest
from fastapi import Response

from authentication import AuthenticationBackend, BearerTransport, Strategy
from authentication.strategy import StrategyDestroyNotSupportedError
from authentication.transport.base import Transport
from db import models_protocol as models
from managers.user import BaseUserManager
from tests.conftest import MockStrategy, MockTransport, UserModel


class MockTransportLogoutNotSupported(BearerTransport):
    pass


class MockStrategyDestroyNotSupported(Strategy, Generic[models.UP, models.SIHE]):
    async def read_token(
        self,
        token: Optional[str],
        user_manager: BaseUserManager[models.UP, models.SIHE, models.OAP, models.UOAP],
    ) -> Optional[models.UP]:
        return None

    async def write_token(self, user: models.UP) -> str:
        return "TOKEN"

    async def destroy_token(self, token: str, user: models.UP) -> None:
        raise StrategyDestroyNotSupportedError


@pytest.fixture(params=[MockTransport, MockTransportLogoutNotSupported])
def transport(request) -> Transport:
    transport_class: type[BearerTransport] = request.param
    return transport_class(token_url="/login")


@pytest.fixture(params=[MockStrategy, MockStrategyDestroyNotSupported])
def get_strategy(request) -> Callable[..., Strategy]:
    strategy_class: type[Strategy] = request.param
    return lambda: strategy_class()


@pytest.fixture
def backend(
    transport: Transport, get_strategy: Callable[..., Strategy]
) -> AuthenticationBackend:
    return AuthenticationBackend(
        name="mock", transport=transport, get_strategy=get_strategy
    )


@pytest.mark.authentication
async def test_logout(backend: AuthenticationBackend, user: UserModel):
    strategy = cast(Strategy, backend.get_strategy())
    result = await backend.logout(strategy, user, "TOKEN")
    assert isinstance(result, Response)
