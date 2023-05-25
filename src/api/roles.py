from typing import Generic, Sequence, Type

from fastapi import APIRouter

from api.v1.roles import get_roles_router
import models as models
import schemas
from authentication import Authenticator, AuthenticationBackend
from services.rights import RoleManagerDependency
from services.user import UserManagerDependency


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
            role_update_schema: Type[schemas.RU]
    ) -> APIRouter:
        """
        Return a router with routes to manage roles.

        :param user_schema: Pydantic schema of a public user.
        :param user_update_schema: Pydantic schema for updating a user.
        """
        return get_roles_router(
            self.get_user_manager,
            role_schema,
            role_update_schema,
            self.authenticator
        )
