from typing import Generic, Sequence

import api.schemas as schemas
import db.models_protocol as models_protocol
from api.v1.rights import APIRouter, get_access_rights_router
from authentication import AuthenticationBackend, Authenticator
from managers.rights import AccessRightManagerDependency
from managers.role import RoleManagerDependency
from managers.user import UserManagerDependency


class APIAccessRight(
    Generic[
        models_protocol.ARP,
        models_protocol.RARP,
        models_protocol.RP,
        models_protocol.UP,
        models_protocol.SIHE,
    ]
):
    authenticator: Authenticator[models_protocol.UP, models_protocol.SIHE]

    def __init__(
        self,
        get_user_manager: UserManagerDependency[
            models_protocol.UP,
            models_protocol.SIHE,
            models_protocol.OAP,
            models_protocol.UOAP,
        ],
        get_role_manager: RoleManagerDependency[
            models_protocol.UP, models_protocol.RP, models_protocol.URP,
        ],
        get_access_rights_manager: AccessRightManagerDependency[
            models_protocol.ARP, models_protocol.RARP,
        ],
        auth_backends: Sequence[
            AuthenticationBackend[models_protocol.UP, models_protocol.SIHE]
        ],
    ):
        self.get_user_manager = get_user_manager
        self.get_role_manager = get_role_manager
        self.get_access_rights_manager = get_access_rights_manager
        self.authenticator = Authenticator(auth_backends, get_user_manager)
        self.current_user = self.authenticator.current_user

    def return_access_rights_router(
        self,
        access_right_schema: type[schemas.AR],
        access_right_create_schema: type[schemas.ARC],
        access_right_update_schema: type[schemas.ARU],
        role_access_right_schema: type[schemas.RAR],
        role_access_right_update_schema: type[schemas.RARU],
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
