from typing import Generic, Sequence, Type

from fastapi import APIRouter

import api.schemas as schemas
from api.v1.roles import get_roles_router
from authentication import AuthenticationBackend, Authenticator
from db import models_protocol
from managers.role import RoleManagerDependency
from managers.user import UserManagerDependency


class APIRoles(Generic[models_protocol.RP, models_protocol.UP, models_protocol.SIHE]):
    authenticator: Authenticator[models_protocol.UP, models_protocol.SIHE]

    def __init__(
        self,
        get_user_manager: UserManagerDependency[
            models_protocol.UP, models_protocol.SIHE
        ],
        get_role_manager: RoleManagerDependency[
            models_protocol.UP, models_protocol.RP, models_protocol.URP,
        ],
        auth_backends: Sequence[
            AuthenticationBackend[models_protocol.UP, models_protocol.SIHE]
        ],
    ):
        self.authenticator = Authenticator(auth_backends, get_user_manager)
        self.get_user_manager = get_user_manager
        self.get_role_manager = get_role_manager
        self.current_user = self.authenticator.current_user

    def get_roles_router(
        self,
        role_schema: type[schemas.R],
        role_create_schema: type[schemas.RC],
        role_update_schema: type[schemas.RU],
        user_role_schema: type[schemas.UR],
        user_role_update_schema: type[schemas.URU],
    ) -> APIRouter:
        """
        Return a router with routes to manage roles.

        :param role_schema: Pydantic schema of a role.
        :param role_create_schema:
        :param role_update_schema: Pydantic schema for updating a role.
        :param user_role_schema: Pydantic schema of a user role entity
        :param user_role_update_schema:
        """
        return get_roles_router(
            self.get_user_manager,
            self.get_role_manager,
            role_schema,
            role_create_schema,
            role_update_schema,
            user_role_schema,
            user_role_update_schema,
            self.authenticator,
        )
