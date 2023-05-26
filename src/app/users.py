from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import Depends, Request, Response

import models
from core.config import settings
from app.auth import auth_backend
from core.pagination import PaginateQueryParams
from models import UUIDIDMixin
from api.auth_users import APIUsers
from schemas import SIHE, BaseSignInHistoryEvent
from services.user import BaseUserManager

from db.users import SQLAlchemyUserDatabase

from app.db import User, get_user_db


class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    reset_password_token_secret = settings.reset_password_token_secret
    verification_token_secret = settings.verification_token_secret

    async def get_sign_in_history(
            self,
            user: User,
            pagination_params: PaginateQueryParams
    ) -> list[models.SignInHistoryEvent]:
        return await self.user_db.get_sign_in_history(user.id, pagination_params)

    async def _record_in_sighin_history(self, user: User, request: Request):
        event = BaseSignInHistoryEvent(
            timestamp=datetime.now(),
            fingerprint=request.client.host
        )
        await self.user_db.record_in_sighin_history(user_id=user.id, event=event)

    async def on_after_login(
            self,
            user: User,
            request: Optional[Request] = None,
            response: Optional[Response] = None,
    ) -> None:
        await self._record_in_sighin_history(user, request)

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
