from fastapi import Depends

from api.roles import APIRoles
from db.roles import SQLAlchemyRoleDatabase, SQLAlchemyUserRoleDatabase
from services.role import BaseRoleManager
from models import UUIDIDMixin

from app.db import User, Role, UUID, get_role_db, get_user_role_db
from app.users import auth_backend, get_user_manager


class RoleManager(UUIDIDMixin, BaseRoleManager[Role, UUID]):
    pass


async def get_role_manager(
        role_db: SQLAlchemyRoleDatabase = Depends(get_role_db),
        user_role_db: SQLAlchemyUserRoleDatabase = Depends(get_user_role_db)
):
    yield RoleManager(role_db, user_role_db=user_role_db)

api_roles = APIRoles[User, UUID](get_user_manager, get_role_manager, [auth_backend])