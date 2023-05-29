from fastapi import Depends

from api.access_rights import APIAccessRight
from api.roles import APIRoles
from app.db import UUID, AccessRight, Role, User, get_access_right_db
from app.services.auth import auth_backend
from app.services.roles import get_role_manager
from app.services.users import get_user_manager
from db.models import UUIDIDMixin
from db.roles import SQLAlchemyRoleDatabase
from managers.rights import BaseAccessRightManager
from managers.role import BaseRoleManager


class AccessRightManager(UUIDIDMixin, BaseAccessRightManager[AccessRight, UUID]):
    pass


async def get_access_right_manager(
    role_db: SQLAlchemyRoleDatabase = Depends(get_access_right_db),
):
    yield AccessRightManager(get_access_right_db)


api_access_rights = APIAccessRight[AccessRight, UUID](
    get_user_manager, get_role_manager, get_access_right_manager, [auth_backend]
)
