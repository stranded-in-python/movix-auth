from typing import Generic

import models
from core.dependency_types import DependencyCallable
from services.user import BaseUserManager, UserManagerDependency


class BaseRoleManager(
    Generic[models.UP, models.RP, models.ID],
    UserManagerDependency
):
    pass


RoleManagerDependency = DependencyCallable[BaseRoleManager[models.UP, models.RP, models.ID]]
