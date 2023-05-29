from typing import Generic, Sequence, Type

from api import schemas
from fastapi import APIRouter

from api.v1.roles import get_roles_router
from authentication import AuthenticationBackend, Authenticator
from db import models
from managers.rights import RoleManagerDependency
from managers.user import UserManagerDependency


class APIRoles(Generic[models.RP, models.ID]):
    authenticator: Authenticator

    def __init__(
        self,
        get_user_manager: UserManagerDependency[models.UP, models.ID],
        get_role_manager: RoleManagerDependency[models.RP, models.ID],
        auth_backends: Sequence[AuthenticationBackend],
    ):
        self.authenticator = Authenticator(auth_backends, get_user_manager)
        self.get_user_manager = get_user_manager
        self.get_role_manager = get_role_manager
        self.current_user = self.authenticator.current_user

    def get_roles_router(
        self,
        role_schema: Type[schemas.R],
        role_create_schema: Type[schemas.RC],
        role_update_schema: Type[schemas.RU],
        user_role_schema: Type[schemas.UR],
        user_role_update_schema: Type[schemas.URU],
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
