import uuid

from api.access_rights import APIAccessRight
from api.auth_users import APIUsers
from api.roles import APIRoles
from db.schemas import schemas
from managers.jwt import auth_backend
from managers.rights import get_access_right_manager
from managers.role import get_role_manager
from managers.user import get_user_manager

api_users = APIUsers[
    schemas.UserRead, schemas.UserCreate, schemas.UserUpdate, schemas.EventRead
](get_user_manager, [auth_backend])

current_active_user = api_users.current_user(active=True)
api_roles = APIRoles[
    schemas.UserRead,
    schemas.UserCreate,
    schemas.UserUpdate,
    schemas.EventRead,
    schemas.RoleRead,
    schemas.UserRoleRead,
    schemas.UserRoleUpdate,
](get_user_manager, get_role_manager, [auth_backend])


api_access_rights = APIAccessRight[
    schemas.UserRead,
    schemas.UserCreate,
    schemas.EventRead,
    schemas.UserUpdate,
    schemas.RoleRead,
    schemas.UserRoleRead,
    schemas.UserRoleUpdate,
    schemas.AccessRight,
    schemas.AccessRightCreate,
    schemas.AccessRightUpdate,
    schemas.RoleAccessRight,
    schemas.RoleAccessRightUpdate,
    uuid.UUID,
](get_user_manager, get_role_manager, get_access_right_manager, [auth_backend])
