import uuid

# from api.access_rights import APIAccessRight
from api.auth_users import APIUsers
# from api.roles import APIRoles
from db.schemas import models
from managers.jwt import auth_backend
# from managers.rights import get_access_right_manager
# from managers.role import get_role_manager
from managers.user import get_user_manager

api_users = APIUsers[
    models.UserRead, models.EventRead
](get_user_manager, [auth_backend])

current_active_user = api_users.current_user(active=True)
# api_roles = APIRoles[
#     models.UserRead,
#     models.UserCreate,
#     models.UserUpdate,
#     models.EventRead,
#     models.RoleRead,
#     models.UserRoleRead,
#     models.UserRoleUpdate,
# ](get_user_manager, get_role_manager, [auth_backend])
#
#
# api_access_rights = APIAccessRight[
#     models.UserRead,
#     models.UserCreate,
#     models.EventRead,
#     models.UserUpdate,
#     models.RoleRead,
#     models.UserRoleRead,
#     models.UserRoleUpdate,
#     models.AccessRight,
#     models.AccessRightCreate,
#     models.AccessRightUpdate,
#     models.RoleAccessRight,
#     models.RoleAccessRightUpdate,
#     uuid.UUID,
# ](get_user_manager, get_role_manager, get_access_right_manager, [auth_backend])
