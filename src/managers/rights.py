from typing import Generic
from uuid import UUID

from fastapi import Depends

from api.access_rights import APIAccessRight
from core.dependency_types import DependencyCallable
from db import access_rights, db, models
from db.models import UUIDIDMixin
from db.roles import SARoleDB
from managers.jwt import auth_backend
from managers.rights import BaseAccessRightManager
from managers.role import get_role_manager
from managers.user import get_user_manager


class BaseAccessRightManager(Generic[models.ARP, models.ID]):
    pass


AccessRightManagerDependency = DependencyCallable[
    BaseAccessRightManager[models.ARP, models.ID]
]


class AccessRightManager(UUIDIDMixin, BaseAccessRightManager[AccessRight, UUID]):
    pass


async def get_access_right_manager(role_db: SARoleDB = Depends(get_access_right_db)):
    yield AccessRightManager()
