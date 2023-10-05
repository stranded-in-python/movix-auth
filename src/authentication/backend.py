from typing import Generic, Iterable
from uuid import UUID

from fastapi import Response, status

from authentication.strategy import Strategy, StrategyDestroyNotSupportedError
from authentication.transport import Transport, TransportLogoutNotSupportedError
from core.dependency_types import DependencyCallable
from db import models_protocol


class AuthenticationBackend(Generic[models_protocol.UP, models_protocol.SIHE]):
    """
    Combination of an authentication transport and strategy.

    Together, they provide a full authentication method logic.

    :param name: Name of the backend.
    :param transport: Authentication transport instance.
    :param get_strategy: Dependency callable returning
    an authentication strategy instance.
    """

    name: str
    transport: Transport

    def __init__(
        self,
        name: str,
        transport: Transport,
        get_strategy: DependencyCallable[
            Strategy[models_protocol.UP, models_protocol.SIHE]
        ],
    ):
        self.name = name
        self.transport = transport
        self.get_strategy = get_strategy

    async def login(
        self,
        strategy: Strategy[models_protocol.UP, models_protocol.SIHE],
        user: models_protocol.UP,
        access_right_ids: Iterable[UUID],
    ) -> Response:
        token = await strategy.write_token(user, access_right_ids)
        return await self.transport.get_login_response(token)

    async def logout(
        self,
        strategy: Strategy[models_protocol.UP, models_protocol.SIHE],
        user: models_protocol.UP,
        token: str,
    ) -> Response:
        try:
            await strategy.destroy_token(token, user)
        except StrategyDestroyNotSupportedError:
            pass

        try:
            response = await self.transport.get_logout_response()
        except TransportLogoutNotSupportedError:
            response = Response(status_code=status.HTTP_204_NO_CONTENT)

        return response
