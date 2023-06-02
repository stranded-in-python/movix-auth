from typing import Generic, Sequence, Type

import db.models as models
from api.v1.rights import APIRouter, get_access_rights_router
from authentication import AuthenticationBackend, Authenticator
from db.schemas import generics
from managers.rights import AccessRightManagerDependency
from managers.role import RoleManagerDependency
from managers.user import UserManagerDependency, UserMgrDependencyType

RoleMgrDependencyType = RoleManagerDependency[
    models.RP, models.URP, generics.RC, generics.RU, models.URUP
]
AccessRightMgrDependencyType = AccessRightManagerDependency[
    models.ARP, generics.ARC, generics.ARU, models.RARP, models.RARUP
]


class APIAccessRight(
    Generic[
        generics.U,
        generics.UC,
        generics.SIHE,
        generics.UU,
        models.RP,
        models.URP,
        models.URUP,
        models.ARP,
        generics.ARC,
        generics.ARU,
        models.RARP,
        models.RARUP,
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
        get_access_rights_manager: AccessRightManagerDependency[
            models.ARP, generics.ARC, generics.ARU, models.RARP, models.RARUP
        ],
        auth_backends: Sequence[AuthenticationBackend],
    ):
        self.get_user_manager = get_user_manager
        self.get_role_manager = get_role_manager
        self.get_access_rights_manager = get_access_rights_manager
        self.authenticator = Authenticator(auth_backends, get_user_manager)
        self.current_user = self.authenticator.current_user

    def get_access_rights_router(
        self,
        access_right_schema: Type[generics.AR],
        access_right_create_schema: Type[generics.ARC],
        access_right_update_schema: Type[generics.ARU],
        role_access_right_schema: Type[generics.RAR],
        role_access_right_update_schema: Type[generics.RARU],
    ) -> APIRouter:
        return get_access_rights_router(
            self.get_user_manager,
            self.get_role_manager,
            self.get_access_rights_manager,
            access_right_schema,
            access_right_create_schema,
            access_right_update_schema,
            role_access_right_schema,
            role_access_right_update_schema,
            self.authenticator,
        )
