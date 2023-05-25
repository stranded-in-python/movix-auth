from fastapi import Depends

from api.access_rights import APIAccessRight
from api.roles import APIRoles
from app.db import User, Role, AccessRight, UUID, get_access_right_db
from app.roles import get_role_manager
from app.users import auth_backend, get_user_manager
from db.roles import SQLAlchemyRoleDatabase
from models import UUIDIDMixin
from services.rights import BaseAccessRightManager
from services.role import BaseRoleManager


class AccessRightManager(UUIDIDMixin, BaseAccessRightManager[AccessRight, UUID]):
    pass


async def get_access_right_manager(role_db: SQLAlchemyRoleDatabase = Depends(get_access_right_db)):
    yield AccessRightManager(get_access_right_db)

api_access_rights = APIAccessRight[AccessRight, UUID](
    get_user_manager,
    get_role_manager,
    get_access_right_manager,
    [auth_backend]
)