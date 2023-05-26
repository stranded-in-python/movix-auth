from typing import Optional
from uuid import UUID

from fastapi import Depends, Request

from app.auth import auth_backend
from models import UUIDIDMixin
from api.auth_users import APIUsers
from services.user import BaseUserManager

from db.users import SQLAlchemyUserDatabase

from app.db import User, get_user_db

SECRET = "SECRET"


class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
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


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


api_users = APIUsers[User, UUID](get_user_manager, [auth_backend])

current_active_user = api_users.current_user(active=True)
