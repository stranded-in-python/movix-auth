from datetime import datetime
from typing import Any, Generic, Optional, Union
from uuid import UUID

import jwt
from auth import auth_backend
from fastapi import Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm

import core.exceptions as exceptions
import core.password.password as pw
from api import schemas
from api.auth_users import APIUsers
from api.schemas import BaseSignInHistoryEvent
from app.db import User, get_user_db
from core.config import settings
from core.dependency_types import DependencyCallable
from core.jwt_utils import SecretType, decode_jwt, generate_jwt
from core.pagination import PaginateQueryParams
from db import models
from db.base import BaseUserDatabase
from db.users import SAUserDB
from managers.user import BaseUserManager

RESET_PASSWORD_TOKEN_AUDIENCE = "fastapi-users:reset"
VERIFY_USER_TOKEN_AUDIENCE = "fastapi-users:verify"


class BaseUserManager(Generic[models.UP, models.SIHE]):
    reset_password_token_secret: SecretType
    reset_password_token_lifetime_seconds: int = 3600
    reset_password_token_audience: str = RESET_PASSWORD_TOKEN_AUDIENCE

    verification_token_secret: SecretType
    verification_token_lifetime_seconds: int = 3600
    verification_token_audience: str = VERIFY_USER_TOKEN_AUDIENCE

    user_db: BaseUserDatabase[models.UP, UUID, models.SIHE]
    password_helper: pw.PasswordHelperProtocol

    def __init__(
        self,
        user_db: BaseUserDatabase[models.UP, UUID, models.SIHE],
        password_helper: Optional[pw.PasswordHelperProtocol] = None,
    ):
        self.user_db = user_db
        if password_helper is None:
            self.password_helper = pw.PasswordHelper()
        else:
            self.password_helper = password_helper

    def parse_id(self, value: Any) -> UUID:
        """
        Parse a value into a correct UUID instance.

        :param value: The value to parse.
        :raises InvalidID: The UUID value is invalid.
        :return: An UUID object.
        """
        raise NotImplementedError()

    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Request | None = None,
    ) -> models.UP:
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_username(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user

    async def get(self, user_id: UUID) -> models.UP:
        user = await self.user_db.get(user_id)

        if user is None:
            raise exceptions.UserNotExists()

        return user

    async def get_by_username(self, username: str) -> models.UP:
        user = await self.user_db.get_by_username(username)

        if user is None:
            raise exceptions.UserNotExists()

        return user

    async def get_by_email(self, email: str) -> models.UP:
        user = await self.user_db.get_by_email(email)

        if user is None:
            raise exceptions.UserNotExists()

        return user

    async def forgot_password(
        self, user: models.UP, request: Optional[Request] = None
    ) -> None:
        if not user.is_active:
            raise exceptions.UserInactive()

        token_data = {
            "sub": str(user.id),
            "password_fgpt": self.password_helper.hash(user.hashed_password),
            "aud": self.reset_password_token_audience,
        }
        token = generate_jwt(
            token_data,
            self.reset_password_token_secret,
            self.reset_password_token_lifetime_seconds,
        )
        await self.on_after_forgot_password(user, token, request)

    async def reset_password(
        self, token: str, password: str, request: Optional[Request] = None
    ) -> models.UP:
        try:
            data = decode_jwt(
                token,
                self.reset_password_token_secret,
                [self.reset_password_token_audience],
            )
        except jwt.PyJWTError:
            raise exceptions.InvalidResetPasswordToken()

        try:
            user_id = data["sub"]
            password_fingerprint = data["password_fgpt"]
        except KeyError:
            raise exceptions.InvalidResetPasswordToken()

        try:
            parsed_id = self.parse_id(user_id)
        except exceptions.InvalidID:
            raise exceptions.InvalidResetPasswordToken()

        user = await self.get(parsed_id)

        valid_password_fingerprint, _ = self.password_helper.verify_and_update(
            user.hashed_password, password_fingerprint
        )
        if not valid_password_fingerprint:
            raise exceptions.InvalidResetPasswordToken()

        if not user.is_active:
            raise exceptions.UserInactive()

        updated_user = await self._update(user, {"password": password})

        await self.on_after_reset_password(user, request)

        return updated_user

    async def update(
        self,
        user_update: schemas.UU,
        user: models.UP,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> models.UP:
        if safe:
            updated_user_data = user_update.create_update_dict()
        else:
            updated_user_data = user_update.create_update_dict_superuser()

        updated_user = await self._update(user, updated_user_data)

        await self.on_after_update(updated_user, updated_user_data, request)
        return updated_user

    async def delete(self, user: models.UP, request: Optional[Request] = None) -> None:
        await self.on_before_delete(user, request)
        await self.user_db.delete(user)
        await self.on_after_delete(user, request)

    async def get_sign_in_history(
        self, user: Union[schemas.UC, models.UP], pagination_params: PaginateQueryParams
    ) -> list[models.SignInHistoryEvent]:
        raise NotImplementedError()

    async def validate_password(
        self, password: str, user: Union[schemas.UC, models.UP]
    ) -> None:
        return

    async def authenticate(
        self, credentials: OAuth2PasswordRequestForm
    ) -> Optional[models.UP]:
        """
        Authenticate and return a user following an email and a password.

        Will automatically upgrade password hash if necessary.

        :param credentials: The user credentials.
        """
        try:
            user = await self.get_by_username(credentials.username)
        except exceptions.UserNotExists:
            # Run the hasher to mitigate timing attack
            # Inspired from Django: https://code.djangoproject.com/ticket/20760
            self.password_helper.hash(credentials.password)
            return None

        verified, updated_password_hash = self.password_helper.verify_and_update(
            credentials.password, user.hashed_password
        )
        if not verified:
            return None
        # Update password hash to a more robust one if needed
        if updated_password_hash is not None:
            await self.user_db.update(user, {"hashed_password": updated_password_hash})

        return user

    async def on_after_register(
        self, user: models.UP, request: Optional[Request] = None
    ) -> None:
        ...

    async def on_after_update(
        self,
        user: models.UP,
        update_dict: dict[str, Any],
        request: Optional[Request] = None,
    ) -> None:
        ...

    async def on_after_request_verify(
        self, user: models.UP, token: str, request: Optional[Request] = None
    ) -> None:
        ...

    async def on_after_verify(
        self, user: models.UP, request: Optional[Request] = None
    ) -> None:
        ...

    async def on_after_forgot_password(
        self, user: models.UP, token: str, request: Optional[Request] = None
    ) -> None:
        ...

    async def on_after_reset_password(
        self, user: models.UP, request: Optional[Request] = None
    ) -> None:
        ...

    async def on_after_login(
        self,
        user: models.UP,
        request: Optional[Request] = None,
        response: Optional[Response] = None,
    ) -> None:
        ...

    async def on_before_delete(
        self, user: models.UP, request: Optional[Request] = None
    ) -> None:
        ...

    async def on_after_delete(
        self, user: models.UP, request: Optional[Request] = None
    ) -> None:
        ...

    async def _update(self, user: models.UP, update_dict: dict[str, Any]) -> models.UP:
        validated_update_dict = {}

        for field, value in update_dict.items():
            if field == "email" and value != user.email:
                try:
                    await self.get_by_email(value)
                    raise exceptions.UserAlreadyExists()
                except exceptions.UserNotExists:
                    validated_update_dict["email"] = value

            elif field == "password":
                await self.validate_password(value, user)
                validated_update_dict["hashed_password"] = self.password_helper.hash(
                    value
                )

            else:
                validated_update_dict[field] = value

        return await self.user_db.update(user, validated_update_dict)


UserManagerDependency = DependencyCallable[BaseUserManager[models.UP, models.SIHE]]


class UserManager(models.UUIDIDMixin, BaseUserManager[User, UUID]):
    reset_password_token_secret = settings.reset_password_token_secret
    verification_token_secret = settings.verification_token_secret

    async def get_sign_in_history(
        self, user: User, pagination_params: PaginateQueryParams
    ) -> list[models.SignInHistoryEvent]:
        return await self.user_db.get_sign_in_history(user.id, pagination_params)

    async def _record_in_sighin_history(self, user: User, request: Request):
        if request.client is None:
            return
        event = BaseSignInHistoryEvent(
            timestamp=datetime.now(), fingerprint=request.client.host
        )
        await self.user_db.record_in_sighin_history(user_id=user.id, event=event)

    async def on_after_login(
        self,
        user: User,
        request: Request | None = None,
        response: Response | None = None,
    ) -> None:
        if not request:
            return
        await self._record_in_sighin_history(user, request)

    async def on_after_register(self, user: User, request: Request | None = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SAUserDB = Depends(get_user_db)):
    yield UserManager(user_db)


api_users = APIUsers[User, UUID](get_user_manager, [auth_backend])

current_active_user = api_users.current_user(active=True)
