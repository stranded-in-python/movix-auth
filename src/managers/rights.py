from typing import Generic
from uuid import UUID

from fastapi import Depends

from api.access_rights import APIAccessRight
from app.services.auth import auth_backend
from app.services.roles import get_role_manager
from app.services.users import get_user_manager
from core.dependency_types import DependencyCallable
from db import access_rights, db, models
from db.models import UUIDIDMixin
from db.roles import SARoleDB
from managers.rights import BaseAccessRightManager


class BaseAccessRightManager(Generic[models.ARP, models.ID]):
    pass


AccessRightManagerDependency = DependencyCallable[
    BaseAccessRightManager[models.ARP, models.ID]
]


class AccessRightManager(UUIDIDMixin, BaseAccessRightManager[AccessRight, UUID]):
    pass


async def get_access_right_manager(role_db: SARoleDB = Depends(get_access_right_db)):
    yield AccessRightManager()


api_access_rights = APIAccessRight[cast(ARP, access_rights.SAAccessRight), UUID](
    get_user_manager, get_role_manager, get_access_right_manager, [auth_backend]
)
