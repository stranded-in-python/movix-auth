import logging
import uuid
from datetime import datetime
from typing import Any, Generic, Iterable, cast

import jwt
from fastapi import Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from httpx_oauth.clients.google import GoogleOAuth2

import core.exceptions as exceptions
import core.password.password as pw
from api import schemas
from core.config import settings
from core.dependency_types import DependencyCallable
from core.jwt_utils import SecretType, decode_jwt, generate_jwt  # type: ignore
from core.logger import logger
from core.pagination import PaginateQueryParams
from db import getters, models_protocol
from db.base import BaseUserDatabase
from db.schemas import models
from db.users import SAUserDB

RESET_PASSWORD_TOKEN_AUDIENCE = "fastapi-users:reset"
VERIFY_USER_TOKEN_AUDIENCE = "fastapi-users:verify"

google_oauth_client = GoogleOAuth2(
    str(settings.google_oauth_client_id), str(settings.google_oauth_client_secret)
)
logger()


class BaseUserManager(
    Generic[
        models_protocol.UP,
        models_protocol.SIHE,
        models_protocol.OAP,
        models_protocol.UOAP,
    ]
):
    reset_password_token_secret: SecretType
    reset_password_token_lifetime_seconds: int = 3600
    reset_password_token_audience: str = RESET_PASSWORD_TOKEN_AUDIENCE

    verification_token_secret: SecretType
    verification_token_lifetime_seconds: int = 3600
    verification_token_audience: str = VERIFY_USER_TOKEN_AUDIENCE

    user_db: BaseUserDatabase[
        models_protocol.UP,
        uuid.UUID,
        models_protocol.SIHE,
        models_protocol.OAP,
        models_protocol.UOAP,
    ]
    password_helper: pw.PasswordHelperProtocol

    def __init__(
        self,
        user_db: BaseUserDatabase[
            models_protocol.UP,
            uuid.UUID,
            models_protocol.SIHE,
            models_protocol.OAP,
            models_protocol.UOAP,
        ],
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
        user_create: schemas.UserCreate,
        safe: bool = False,
        request: Request | None = None,
    ) -> models_protocol.UP:
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user:
            logging.exception("UserAlreadyexists: %s" % user_create.email)
            raise exceptions.UserAlreadyExists()
        existing_user = (
            await self.user_db.get_by_username(user_create.username)
            if user_create.username
            else None
        )
        if existing_user:
            logging.exception("UserAlreadyexists: %s" % user_create.username)
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

    async def reset_password(  # noqa: C901
        self, token: str, password: str, request: Request | None = None
    ) -> models_protocol.UP:
        try:
            data = decode_jwt(
                token,
                self.reset_password_token_secret,
                [self.reset_password_token_audience],
            )
        except jwt.PyJWTError:
            logging.exception("InvalidResetPasswordToken:%s" % token)
            raise exceptions.InvalidResetPasswordToken()

        try:
            user_id = data["sub"]
            password_fingerprint = data["password_fgpt"]
        except KeyError:
            logging.exception("InvalidResetPasswordToken:fingerprint:nofingerprint!")
            raise exceptions.InvalidResetPasswordToken()

        try:
            parsed_id = self.parse_id(user_id)
        except exceptions.InvalidID:
            logging.exception("InvalidResetPasswordToken:invalidid:%s" % user_id)
            raise exceptions.InvalidResetPasswordToken()

        user = await self.get(parsed_id)

        valid_password_fingerprint, _ = self.password_helper.verify_and_update(
            user.hashed_password, password_fingerprint
        )
        if not valid_password_fingerprint:
            logging.exception(
                "InvalidResetPasswordToken:validpasswordfingerprint:%s" % parsed_id
            )
            raise exceptions.InvalidResetPasswordToken()

        if not user.is_active:
            logging.exception("UserInactive:%s" % parsed_id)
            raise exceptions.UserInactive()

        updated_user = await self._update(user, {"password": password})

        await self.on_after_reset_password(user, request)

        return updated_user

    async def update(
        self,
        user_update: schemas.UserUpdate,
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

    async def delete(
        self, user: models_protocol.UP, request: Request | None = None
    ) -> None:
        await self.on_before_delete(user, request)
        await self.user_db.delete(user)
        await self.on_after_delete(user, request)

    async def get_sign_in_history(
        self, user: models_protocol.UP, pagination_params: PaginateQueryParams
    ) -> Iterable[models_protocol.SIHE]:
        raise NotImplementedError()

    async def validate_password(
        self, password: str, user: schemas.UserCreate | models_protocol.UP
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
            await self.user_db.update(user, {"hashed_password": updated_password_hash})

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

    async def _update(
        self, user: models_protocol.UP, update_dict: dict[str, Any]
    ) -> models_protocol.UP:
        validated_update_dict = {}

        for field, value in update_dict.items():
            if field == "email" and value != user.email:
                try:
                    await self.get_by_email(value)
                    logging.exception("UserAlreadyExists:%s" % user.email)
                    raise exceptions.UserAlreadyExists()
                except exceptions.UserNotExists:
                    logging.exception("UserNotExists: %s" % user.email)
                    validated_update_dict["email"] = value

            elif field == "password":
                await self.validate_password(value, user)
                validated_update_dict["hashed_password"] = self.password_helper.hash(
                    value
                )

            else:
                validated_update_dict[field] = value

        return await self.user_db.update(user, validated_update_dict)

    async def get_by_oauth_account(
        self, oauth: str, account_id: str
    ) -> models_protocol.UOAP:
        """
        Get a user by OAuth account.

        :param oauth: Name of the OAuth client.
        :param account_id: Id. of the account on the external OAuth service.
        :raises UserNotExists: The user does not exist.
        :return: A user.
        """
        user = await self.user_db.get_by_oauth_account(oauth, account_id)

        if user is None:
            raise exceptions.UserNotExists()

        return user

    async def oauth_callback(
        self,
        oauth_name: str,
        access_token: str,
        account_id: str,
        account_email: str,
        expires_at: int | None = None,
        refresh_token: str | None = None,
        request: Request | None = None,
        *,
        associate_by_email: bool = False,
    ) -> models_protocol.UOAP:
        """
        Handle the callback after a successful OAuth authentication.

        If the user already exists with this OAuth account, the token is updated.

        If a user with the same e-mail already exists and `associate_by_email` is True,
        the OAuth account is associated to this user.
        Otherwise, the `UserNotExists` exception is raised.

        If the user does not exist, it is created and the on_after_register handler
        is triggered.

        :param oauth_name: Name of the OAuth client.
        :param access_token: Valid access token for the service provider.
        :param account_id: models.ID of the user on the service provider.
        :param account_email: E-mail of the user on the service provider.
        :param expires_at: Optional timestamp at which the access token expires.
        :param refresh_token: Optional refresh token to get a
        fresh access token from the service provider.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None
        :param associate_by_email: If True, any existing user with the same
        e-mail address will be associated to this user. Defaults to False.
        :return: A user.
        """
        oauth_account_dict = {
            "oauth_name": oauth_name,
            "access_token": access_token,
            "account_id": account_id,
            "account_email": account_email,
            "expires_at": expires_at,
            "refresh_token": refresh_token,
        }

        try:
            user = await self.get_by_oauth_account(oauth_name, account_id)
        except exceptions.UserNotExists:
            try:
                # Associate account
                user = await self.get_by_email(account_email)
                if not associate_by_email:
                    raise exceptions.UserAlreadyExists()
                user = await self.user_db.add_oauth_account(user, oauth_account_dict)
            except exceptions.UserNotExists:
                # Create account
                password = self.password_helper.generate()
                user_dict = {
                    "email": account_email,
                    "username": account_email.split("@")[0],
                    "hashed_password": self.password_helper.hash(password),
                }
                _user = await self.user_db.create(user_dict)
                user = await self.user_db.add_oauth_account(_user, oauth_account_dict)
                await self.on_after_register(_user, request)
        else:
            # Update oauth
            if not hasattr(user, "oauth_accounts"):
                raise exceptions.AppException("Add oauth_accounts to the db schema")

            user = cast(models_protocol.UserOAuthProtocol, user)

            for existing_oauth_account in user.oauth_accounts:
                if (
                    existing_oauth_account.account_id == account_id
                    and existing_oauth_account.oauth_name == oauth_name
                ):
                    user = cast(models_protocol.UOAP, user)
                    user = await self.user_db.update_oauth_account(
                        user, existing_oauth_account, oauth_account_dict
                    )
            user = cast(models_protocol.UOAP, user)
        return user


UserManagerDependency = DependencyCallable[
    BaseUserManager[
        models_protocol.UP,
        models_protocol.SIHE,
        models_protocol.OAP,
        models_protocol.UOAP,
    ]
]


class UserManager(
    models_protocol.UUIDIDMixin,
    BaseUserManager[
        models_protocol.UP,
        models_protocol.SIHE,
        models_protocol.OAP,
        models_protocol.UOAP,
    ],
):
    reset_password_token_secret = settings.reset_password_token_secret
    verification_token_secret = settings.verification_password_token_secret

    async def get_sign_in_history(
        self, user: models.UserRead, pagination_params: PaginateQueryParams
    ) -> Iterable[models_protocol.SIHE]:
        return await self.user_db.get_sign_in_history(user.id, pagination_params)

    async def _record_in_sighin_history(self, user: models.UserRead, request: Request):
        if request.client is None:
            return
        event = cast(
            models_protocol.SIHE,
            models.EventRead(
                id=uuid.uuid4(),
                user_id=user.id,
                timestamp=datetime.now(),
                fingerprint=request.client.host,
            ),
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
        logging.info("%s registered" % user.id)

    async def on_after_forgot_password(
        self, user: models.UserRead, token: str, request: Request | None = None
    ):
        logging.info("%s forgot password. Reset token:%s" % user.id, token)


async def get_user_manager(user_db: SAUserDB = Depends(getters.get_user_db)):
    yield UserManager(user_db)
