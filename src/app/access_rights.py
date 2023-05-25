from api.roles import APIRoles
from app.db import User, Role, UUID
from models import UUIDIDMixin
from services.role import BaseRoleManager


class RoleManager(UUIDIDMixin, BaseRoleManager[Role, UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_role_manager(role_db: SQLAlchemyRoleDatabase = Depends(get_role_db)):
    yield RoleManager(user_db)

api_users = APIRoles[User, Role, UUID](get_role_manager, [auth_backend])