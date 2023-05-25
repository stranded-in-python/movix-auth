from typing import Generic, Sequence

import models as models
from authentication import Authenticator, AuthenticationBackend
from services.rights import AccessRightManagerDependency
from services.role import RoleManagerDependency
from services.user import UserManagerDependency


class APIAccessRight(Generic[models.RP, models.RP, models.ARP, models.ID]):
    authenticator: Authenticator

    def __init__(
            self,
            get_user_manager: UserManagerDependency[models.UP, models.ID],
            get_role_manager: RoleManagerDependency[models.UP, models.PR, models.ID],
            get_access_rights_manager: AccessRightManagerDependency[models.UP, models.RP, models.ARP, models.ID],
            auth_backends: Sequence[AuthenticationBackend],
    ):
        self.get_user_manager = get_user_manager
        self.get_role_manager = get_role_manager
        self.get_access_rights_manager = get_access_rights_manager
        self.authenticator = Authenticator(auth_backends, get_user_manager)
        self.current_user = self.authenticator.current_user
