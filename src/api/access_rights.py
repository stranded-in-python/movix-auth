from typing import Generic, Sequence

import db.models as models
from authentication import AuthenticationBackend, Authenticator
from managers.rights import AccessRightManagerDependency
from managers.role import RoleManagerDependency
from managers.user import UserManagerDependency


class APIAccessRight(Generic[models.ARP, models.ID]):
    authenticator: Authenticator

    def __init__(
        self,
        get_user_manager: UserManagerDependency[models.UP, models.ID],
        get_role_manager: RoleManagerDependency[models.RP, models.ID],
        get_access_rights_manager: AccessRightManagerDependency[models.ARP, models.ID],
        auth_backends: Sequence[AuthenticationBackend],
    ):
        self.get_user_manager = get_user_manager
        self.get_role_manager = get_role_manager
        self.get_access_rights_manager = get_access_rights_manager
        self.authenticator = Authenticator(auth_backends, get_user_manager)
        self.current_user = self.authenticator.current_user
