from typing import Generic

import models
from core.dependency_types import DependencyCallable
from services.user import BaseUserManager, UserManagerDependency


class BaseRoleManager(
    Generic[models.RP, models.ID]
):
    def __init__(self):
        pass


RoleManagerDependency = DependencyCallable[BaseRoleManager[models.RP, models.ID]]
