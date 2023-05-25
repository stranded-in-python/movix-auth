from typing import Optional, Union, Any, Generic
import jwt

from fastapi import Request, Response

from core.dependency_types import DependencyCallable
from core.pagination import PaginateQueryParams
from db.base import BaseUserDatabase
import models as models
import core.exceptions as exceptions
import schemas as schemas
import password.password as pw
from core.jwt_utils import SecretType, decode_jwt, generate_jwt


RESET_PASSWORD_TOKEN_AUDIENCE = "fastapi-users:reset"
VERIFY_USER_TOKEN_AUDIENCE = "fastapi-users:verify"


class BaseUserManager(Generic[models.UP, models.ID]):
    reset_password_token_secret: SecretType
    reset_password_token_lifetime_seconds: int = 3600
    reset_password_token_audience: str = RESET_PASSWORD_TOKEN_AUDIENCE

    verification_token_secret: SecretType
    verification_token_lifetime_seconds: int = 3600
    verification_token_audience: str = VERIFY_USER_TOKEN_AUDIENCE

    user_storage: BaseUserDatabase[models.UP, models.ID]
    password_helper: pw.PasswordHelperProtocol

    def __init__(
        self,
        user_storage: BaseUserDatabase[models.UP, models.ID],
        password_helper: Optional[pw.PasswordHelperProtocol] = None,
    ):
        self.user_storage = user_storage
        if password_helper is None:
            self.password_helper = pw.PasswordHelper()
        else:
            self.password_helper = password_helper

    def parse_id(self, value: Any) -> models.ID:
        """
        Parse a value into a correct models.ID instance.
        Must implement in Generic[models.ID]
        
        :param value: The value to parse.
        :raises InvalidID: The models.ID value is invalid.
        :return: An models.ID object.
        """
        raise NotImplementedError()

    async def create(
            self,
            user_create: schemas.UC,
            safe: bool = False,
            request: Request | None = None
    ) -> models.UP:

        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_storage.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        created_user = await self.user_storage.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user

    async def get(self, user_id: models.ID) -> models.UP:
        user = await self.user_storage.get(user_id)

        if user is None:
            raise exceptions.UserNotExists()

        return user

    async def get_by_email(self, user_email: str) -> models.UP:

        user = await self.user_storage.get_by_email(user_email)

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

        updated_user = await self._update(user, {"pw": password})

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

    async def delete(
            self,
            user: models.UP,
            request: Optional[Request] = None,
    ) -> None:

        await self.on_before_delete(user, request)
        await self.user_storage.delete(user)
        await self.on_after_delete(user, request)

    async def get_sign_in_history(
            self,
            user: Union[schemas.UC, models.UP],
            pagination_params: PaginateQueryParams
    ) -> list[models.SignInHistoryEvent]:
        ...

    async def validate_password(
            self, password: str, user: Union[schemas.UC, models.UP]
    ) -> None:

        return

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
                    validated_update_dict["is_verified"] = False

            elif field == "pw":
                await self.validate_password(value, user)
                validated_update_dict["hashed_password"] = self.password_helper.hash(
                    value
                )

            else:
                validated_update_dict[field] = value

        return await self.user_db.update(user, validated_update_dict)


UserManagerDependency = DependencyCallable[BaseUserManager[models.UP, models.ID]]
