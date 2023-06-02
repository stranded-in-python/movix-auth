from typing import Generic, Sequence, Type

from fastapi import APIRouter

from api.v1.roles import get_roles_router
from authentication import AuthenticationBackend, Authenticator
from db import models
from db.schemas import generics
from managers.role import RoleManagerDependency
from managers.user import UserManagerDependency


class APIRoles(
    Generic[
        generics.U,
        generics.UC,
        generics.UU,
        generics.SIHE,
        models.RP,
        models.URP,
        models.URUP,
    ]
):
    authenticator: Authenticator

    def __init__(
        self,
        get_user_manager: UserManagerDependency[
            generics.U, generics.UC, generics.UU, generics.SIHE
        ],
        get_role_manager: RoleManagerDependency[
            models.RP, models.URP, generics.RC, generics.RU, models.URUP
        ],
        auth_backends: Sequence[AuthenticationBackend],
    ):
        self.authenticator = Authenticator(auth_backends, get_user_manager)
        self.get_user_manager = get_user_manager
        self.get_role_manager = get_role_manager
        self.current_user = self.authenticator.current_user

    def get_roles_router(
        self,
        role_schema: Type[generics.R],
        role_create_schema: Type[generics.RC],
        role_update_schema: Type[generics.RU],
        user_role_schema: Type[generics.UR],
        user_role_update_schema: Type[generics.URU],
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
