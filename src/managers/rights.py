from typing import Generic

from core.dependency_types import DependencyCallable
from db import models
from managers.role import RoleManagerDependency
from managers.user import UserManagerDependency


class BaseAccessRightManager(Generic[models.ARP, models.ID]):
    pass


AccessRightManagerDependency = DependencyCallable[
    BaseAccessRightManager[models.ARP, models.ID]
]
