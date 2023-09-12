from typing import Generic, Sequence

from fastapi import APIRouter
from httpx_oauth.oauth2 import BaseOAuth2

from api import schemas
from api.oauth import get_oauth_router
from api.v1.auth import get_auth_router
from api.v1.register import get_register_router
from api.v1.reset import get_reset_password_router
from api.v1.user import get_users_me_router, get_users_router
from api.v1.verify import get_verify_router
from authentication import AuthenticationBackend, Authenticator
from core.jwt_utils import SecretType
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

    access_authenticator: Authenticator[models_protocol.UP, models_protocol.SIHE]
    refresh_authenticator: Authenticator[models_protocol.UP, models_protocol.SIHE]

    def __init__(
        self,
        get_user_manager: UserManagerDependency[
            models_protocol.UP,
            models_protocol.SIHE,
            models_protocol.OAP,
            models_protocol.UOAP,
        ],
        access_backends: Sequence[
            AuthenticationBackend[models_protocol.UP, models_protocol.SIHE]
        ],
        refresh_backends: Sequence[
            AuthenticationBackend[models_protocol.UP, models_protocol.SIHE]
        ],
        user_channels_schema: type[schemas.UCH],
        channel_schema: type[schemas.CH],
    ):
        self.access_authenticator = Authenticator(access_backends, get_user_manager)
        self.refresh_authenticator = Authenticator(refresh_backends, get_user_manager)
        self.get_user_manager = get_user_manager
        self.current_user = self.access_authenticator.current_user
        self.auth_current_user = self.refresh_authenticator.current_user
        self.user_channels_schema = user_channels_schema
        self.channel_schema = channel_schema

    def return_register_router(
        self, user_schema: type[schemas.U], user_create_schema: type[schemas.UC]
    ) -> APIRouter:
        """
        Return a router with a register route.

        :param user_schema: Pydantic schema of a public user.
        :param user_create_schema: Pydantic schema for creating a user.
        """
        return get_register_router(
            self.get_user_manager, user_schema, user_create_schema
        )

    def return_reset_password_router(self) -> APIRouter:
        """Return a reset pw process router."""
        return get_reset_password_router(self.get_user_manager)

    def return_auth_router(
        self,
        access_backend: AuthenticationBackend[models_protocol.UP, models_protocol.SIHE],
        refresh_backend: AuthenticationBackend[
            models_protocol.UP, models_protocol.SIHE
        ],
        requires_verification: bool = False,
    ) -> APIRouter:
        """
        Return an auth router for a given authentication backend.

        :param backend: The authentication backend instance.
        :param requires_verification: Whether the authentication
        require the user to be verified or not. Defaults to False.
        """
        return get_auth_router(
            access_backend,
            refresh_backend,
            self.get_user_manager,
            self.access_authenticator,
            self.refresh_authenticator,
            requires_verification,
        )

    def return_users_me_router(
        self,
        user_schema: type[schemas.UserRead],
        user_update_schema: type[schemas.UserUpdate],
        event_schema: type[schemas.EventRead],
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
            self.access_authenticator,
        )

    def return_users_router(
        self,
        user_schema: type[schemas.UserRead],
        user_update_schema: type[schemas.UserUpdate],
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
            self.user_channels_schema,
            self.channel_schema,
            self.access_authenticator,
        )

    def return_oauth_router(
        self,
        oauth_client: BaseOAuth2,
        backend: AuthenticationBackend,
        state_secret: SecretType,
        redirect_url: str | None = None,
        associate_by_email: bool = False,
    ) -> APIRouter:
        """
        Return an OAuth router for a given OAuth client and authentication backend.

        :param oauth_client: The HTTPX OAuth client instance.
        :param backend: The authentication backend instance.
        :param state_secret: Secret used to encode the state JWT.
        :param redirect_url: Optional arbitrary redirect URL for the OAuth2 flow.
        If not given, the URL to the callback endpoint will be generated.
        :param associate_by_email: If True, any existing user with the same
        e-mail address will be associated to this user. Defaults to False.
        """
        return get_oauth_router(
            oauth_client,
            backend,
            self.get_user_manager,
            state_secret,
            redirect_url,
            associate_by_email,
        )

    def return_verify_router(self, user_schema: type[schemas.UserRead]) -> APIRouter:
        return get_verify_router(self.get_user_manager, user_schema)
