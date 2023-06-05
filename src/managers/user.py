import uuid
from datetime import datetime
from typing import Any, Generic, Iterable

import jwt
from fastapi import Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm

from api import schemas
import core.exceptions as exceptions
import core.password.password as pw
from core.config import settings
from core.dependency_types import DependencyCallable
from core.jwt_utils import SecretType, decode_jwt, generate_jwt
from core.pagination import PaginateQueryParams
from db import getters, models_protocol
from db.base import BaseUserDatabase
from db.schemas import generics, models
from db.users import SAUserDB

RESET_PASSWORD_TOKEN_AUDIENCE = "fastapi-users:reset"
VERIFY_USER_TOKEN_AUDIENCE = "fastapi-users:verify"


class BaseUserManager(Generic[models_protocol.UP, models_protocol.SIHE]):
    reset_password_token_secret: SecretType
    reset_password_token_lifetime_seconds: int = 3600
    reset_password_token_audience: str = RESET_PASSWORD_TOKEN_AUDIENCE

    verification_token_secret: SecretType
    verification_token_lifetime_seconds: int = 3600
    verification_token_audience: str = VERIFY_USER_TOKEN_AUDIENCE

    user_db: BaseUserDatabase[models_protocol.UP, uuid.UUID, models_protocol.SIHE]
    password_helper: pw.PasswordHelperProtocol

    def __init__(
        self,
        user_db: BaseUserDatabase[models_protocol.UP, uuid.UUID, models_protocol.SIHE],
        password_helper: pw.PasswordHelperProtocol | None = None,
    ):
        self.user_db = user_db
        if password_helper is None:
            self.password_helper = pw.PasswordHelper()
        else:
            self.password_helper = password_helper

    def parse_id(self, value: Any) -> uuid.UUID:
        """
        Parse a value into a correct uuid.UUID instance.

        :param value: The value to parse.
        :raises InvalidID: The uuid.UUID value is invalid.
        :return: An uuid.UUID object.
        """
        raise NotImplementedError()

    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Request | None = None,
    ) -> models_protocol.UP:
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict() if safe else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user

    async def get(self, user_id: uuid.UUID) -> models_protocol.UP:
        user = await self.user_db.get(user_id)

        if user is None:
            raise exceptions.UserNotExists()

        return user

    async def get_by_username(self, username: str) -> models_protocol.UP:
        user = await self.user_db.get_by_username(username)

        if user is None:
            raise exceptions.UserNotExists()

        return user

    async def get_by_email(self, email: str) -> models_protocol.UP:
        user = await self.user_db.get_by_email(email)

        if user is None:
            raise exceptions.UserNotExists()

        return user

    async def forgot_password(
        self, user: models_protocol.UP, request: Request | None = None
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
        self, token: str, password: str, request: Request | None = None
    ) -> models_protocol.UP:
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
        user: models_protocol.UP,
        safe: bool = False,
        request: Request | None = None,
    ) -> models_protocol.UP:
        if safe:
            updated_user_data = user_update.create_update_dict()
        else:
            updated_user_data = user_update.create_update_dict_superuser()

        updated_user = await self._update(user, updated_user_data)

        await self.on_after_update(updated_user, updated_user_data, request)
        return updated_user

    async def delete(self, user: models_protocol.UP, request: Request | None = None) -> None:
        await self.on_before_delete(user, request)
        await self.user_db.delete(user.id)
        await self.on_after_delete(user, request)

    async def get_sign_in_history(
        self, user: generics.UC | models_protocol.UP, pagination_params: PaginateQueryParams
    ) -> Iterable[models_protocol.SIHE]:
        raise NotImplementedError()

    async def validate_password(
        self, password: str, user: schemas.UC | models_protocol.UP
    ) -> None:
        return

    async def authenticate(
        self, credentials: OAuth2PasswordRequestForm
    ) -> models_protocol.UP | None:
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
        if updated_password_hash:
            await self.user_db.update(user.id, {"hashed_password": updated_password_hash})

        return user

    async def on_after_register(
        self, user: models_protocol.UP, request: Request | None = None
    ) -> None:
        ...

    async def on_after_update(
        self,
        user: models_protocol.UP,
        update_dict: dict[str, Any],
        request: Request | None = None,
    ) -> None:
        ...

    async def on_after_request_verify(
        self, user: models_protocol.UP, token: str, request: Request | None = None
    ) -> None:
        ...

    async def on_after_verify(
        self, user: models_protocol.UP, request: Request | None = None
    ) -> None:
        ...

    async def on_after_forgot_password(
        self, user: models_protocol.UP, token: str, request: Request | None = None
    ) -> None:
        ...

    async def on_after_reset_password(
        self, user: models_protocol.UP, request: Request | None = None
    ) -> None:
        ...

    async def on_after_login(
        self,
        user: models_protocol.UP,
        request: Request | None = None,
        response: Response | None = None,
    ) -> None:
        ...

    async def on_before_delete(
        self, user: models_protocol.UP, request: Request | None = None
    ) -> None:
        ...

    async def on_after_delete(
        self, user: models_protocol.UP, request: Request | None = None
    ) -> None:
        ...

    async def _update(self, user: models_protocol.UP, update_dict: dict[str, Any]) -> models_protocol.UP:
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

        return await self.user_db.update(user.id, validated_update_dict)


UserManagerDependency = DependencyCallable[
    BaseUserManager[models_protocol.UP,  models_protocol.SIHE]
]
UserMgrType = BaseUserManager[generics.U, generics.SIHE]
UserMgrDependencyType = UserManagerDependency[
    generics.U, generics.SIHE
]


class UserManager(
    models_protocol.UUIDIDMixin,
    BaseUserManager[
        models.UserRead, models.EventRead
    ],
):
    reset_password_token_secret = settings.reset_password_token_secret
    verification_token_secret = settings.verification_token_secret

    async def get_sign_in_history(
        self, user: models.UserRead, pagination_params: PaginateQueryParams
    ) -> Iterable[models_protocol.SignInHistoryEvent]:
        return await self.user_db.get_sign_in_history(user.id, pagination_params)

    async def _record_in_sighin_history(self, user: models.UserRead, request: Request):
        if request.client is None:
            return
        event = models.EventRead(
            id=uuid.uuid4(),
            user_id=user.id,
            timestamp=datetime.now(),
            fingerprint=request.client.host,
        )
        await self.user_db.record_in_sighin_history(user_id=user.id, event=event)

    async def on_after_login(
        self,
        user: models.UserRead,
        request: Request | None = None,
        response: Response | None = None,
    ) -> None:
        if not request:
            return
        await self._record_in_sighin_history(user, request)

    async def on_after_register(
        self, user: models.UserRead, request: Request | None = None
    ):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: models.UserRead, token: str, request: Request | None = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: models.UserRead, token: str, request: Request | None = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SAUserDB = Depends(getters.get_user_db)):
    yield UserManager(user_db)
