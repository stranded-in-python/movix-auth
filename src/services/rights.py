from typing import Generic

import models
from core.dependency_types import DependencyCallable
from services.role import RoleManagerDependency
from services.user import UserManagerDependency


class BaseAccessRightManager(
    Generic[models.ARP, models.ID],
    UserManagerDependency,
    RoleManagerDependency
):
    pass


AccessRightManagerDependency = DependencyCallable[BaseAccessRightManager[models.UP, models.RP, models.ARP, models.ID]]
