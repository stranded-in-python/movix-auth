from typing import Generic, Sequence, Type

from fastapi import APIRouter

from api import schemas
from api.v1.auth import get_auth_router
from api.v1.register import get_register_router
from api.v1.reset import get_reset_password_router
from api.v1.user import get_users_me_router, get_users_router
from authentication import AuthenticationBackend, Authenticator
from db import models_protocol
from managers.user import UserManagerDependency


class APIUsers(Generic[models_protocol.UP, models_protocol.SIHE]):
    """
    Main object that ties together the component for users authentication.

    :param get_user_manager: Dependency callable getter to inject the
    user manager class instance.
    :param auth_backends: List of authentication backends.

    :var current_user: Dependency callable getter to inject authenticated user
    with a specific set of parameters.
    """

    authenticator: Authenticator[models_protocol.UP, models_protocol.SIHE]

    def __init__(
        self,
        get_user_manager: UserManagerDependency[
            models_protocol.UP, models_protocol.SIHE
        ],
        auth_backends: Sequence[AuthenticationBackend[models_protocol.UP, models_protocol.SIHE]],
    ):
        self.authenticator = Authenticator(auth_backends, get_user_manager)
        self.get_user_manager = get_user_manager
        self.current_user = self.authenticator.current_user

    def get_register_router(
        self, user_schema: Type[schemas.U], user_create_schema: Type[schemas.UC]
    ) -> APIRouter:
        """
        Return a router with a register route.

        :param user_schema: Pydantic schema of a public user.
        :param user_create_schema: Pydantic schema for creating a user.
        """
        return get_register_router(
            self.get_user_manager, user_schema, user_create_schema
        )

    def get_reset_password_router(self) -> APIRouter:
        """Return a reset pw process router."""
        return get_reset_password_router(self.get_user_manager)

    def get_auth_router(
        self, backend: AuthenticationBackend[models_protocol.UP, models_protocol.SIHE], requires_verification: bool = False
    ) -> APIRouter:
        """
        Return an auth router for a given authentication backend.

        :param backend: The authentication backend instance.
        :param requires_verification: Whether the authentication
        require the user to be verified or not. Defaults to False.
        """
        return get_auth_router(
            backend, self.get_user_manager, self.authenticator, requires_verification
        )

    def get_users_me_router(
        self,
        user_schema: Type[schemas.UserRead],
        user_update_schema: Type[schemas.UserUpdate],
        event_schema: Type[schemas.EventRead],
    ) -> APIRouter:
        """
        Return a router with routes to manage users.

        :param user_schema: Pydantic schema of a public user.
        :param user_update_schema: Pydantic schema for updating a user.
        :param event_schema: Pydantic schema for event of user sign-in.
        """
        return get_users_me_router(
            self.get_user_manager,
            user_schema,
            user_update_schema,
            event_schema,
            self.authenticator,
        )

    def get_users_router(
        self,
        user_schema: Type[schemas.UserRead],
        user_update_schema: Type[schemas.UserUpdate],
    ) -> APIRouter:
        """
        Return a router with routes to manage users.

        :param user_schema: Pydantic schema of a public user.
        :param user_update_schema: Pydantic schema for updating a user.
        :param event_schema: Pydantic schema for event of user sign-in.
        """
        return get_users_router(
            self.get_user_manager,
            user_schema,
            user_update_schema,
            self.authenticator,
        )
