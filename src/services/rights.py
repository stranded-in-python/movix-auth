from typing import Generic

import models
from core.dependency_types import DependencyCallable
from services.role import RoleManagerDependency
from services.user import UserManagerDependency


class BaseAccessRightManager(
    Generic[models.ARP, models.ID]
):
    pass


AccessRightManagerDependency = DependencyCallable[BaseAccessRightManager[models.ARP, models.ID]]
