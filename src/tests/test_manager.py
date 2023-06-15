from typing import Callable

import pytest
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import UUID4
from pytest_mock import MockerFixture

from api import schemas
from authentication.strategy.jwt import decode_jwt, generate_jwt
from core.exceptions import (
    InvalidID,
    InvalidPasswordException,
    InvalidResetPasswordToken,
    InvalidVerifyToken,
    UserAlreadyExists,
    UserAlreadyVerified,
    UserInactive,
    UserNotExists,
)
from db.models_protocol import IntegerIDMixin
from tests.conftest import SignInModel, UserManagerMock, UserModel, UserOAuth, OAuthAccount


@pytest.fixture
def verify_token(user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount]):
    def _verify_token(
        user_id=None,
        email=None,
        lifetime=user_manager.verification_token_lifetime_seconds,
    ):
        data = {"aud": user_manager.verification_token_audience}
        if user_id is not None:
            data["sub"] = str(user_id)
        if email is not None:
            data["email"] = email
        return generate_jwt(data, user_manager.verification_token_secret, lifetime)

    return _verify_token


@pytest.fixture
def forgot_password_token(user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount]):
    def _forgot_password_token(
        user_id=None,
        current_password_hash=None,
        lifetime=user_manager.reset_password_token_lifetime_seconds,
    ):
        data = {"aud": user_manager.reset_password_token_audience}
        if user_id is not None:
            data["sub"] = str(user_id)
        if current_password_hash is not None:
            data["password_fgpt"] = user_manager.password_helper.hash(
                current_password_hash
            )
        return generate_jwt(data, user_manager.reset_password_token_secret, lifetime)

    return _forgot_password_token


@pytest.mark.asyncio
@pytest.mark.manager
class TestGet:
    async def test_not_existing_user(
        self, user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount]
    ):
        with pytest.raises(UserNotExists):
            await user_manager.get(UUID4("d35d213e-f3d8-4f08-954a-7e0d1bea286f"))

    async def test_existing_user(
        self, user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount], user: UserModel
    ):
        retrieved_user = await user_manager.get(user.id)
        assert retrieved_user.id == user.id


@pytest.mark.asyncio
@pytest.mark.manager
class TestGetByEmail:
    async def test_not_existing_user(
        self, user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount]
    ):
        with pytest.raises(UserNotExists):
            await user_manager.get_by_email("lancelot@camelot.bt")

    async def test_existing_user(
        self, user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount], user: UserModel
    ):
        retrieved_user = await user_manager.get_by_email(user.email)
        assert retrieved_user.id == user.id


@pytest.mark.asyncio
@pytest.mark.manager
class TestCreateUser:
    @pytest.mark.parametrize(
        "email", ["king.arthur@camelot.bt", "King.Arthur@camelot.bt"]
    )
    async def test_existing_user(
        self, email: str, user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount]
    ):
        user = schemas.UserCreate(
            email=email,
            password="guinevere",
            first_name="arthur",
            last_name="king",
            username="kingarthur",
        )
        with pytest.raises(UserAlreadyExists):
            await user_manager.create(user)
        assert user_manager.on_after_register.called is False

    @pytest.mark.parametrize("email", ["lancelot@camelot.bt", "Lancelot@camelot.bt"])
    async def test_regular_user(
        self, email: str, user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount]
    ):
        user = schemas.UserCreate(email=email, password="guinevere")
        created_user = await user_manager.create(user)
        assert type(created_user) == UserModel

        assert user_manager.on_after_register.called is True

    @pytest.mark.parametrize("safe,result", [(True, False), (False, True)])
    async def test_superuser(
        self,
        user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount],
        safe: bool,
        result: bool,
    ):
        user = schemas.UserCreate(
            email="lancelot@camelot.b", password="guinevere", is_superuser=True
        )
        created_user = await user_manager.create(user, safe)
        assert type(created_user) == UserModel
        assert created_user.is_superuser is result

        assert user_manager.on_after_register.called is True

    @pytest.mark.parametrize("safe,result", [(True, True), (False, False)])
    async def test_is_active(
        self,
        user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount],
        safe: bool,
        result: bool,
    ):
        user = schemas.UserCreate(
            email="lancelot@camelot.b", password="guinevere", is_active=False
        )
        created_user = await user_manager.create(user, safe)
        assert type(created_user) == UserModel
        assert created_user.is_active is result

        assert user_manager.on_after_register.called is True


@pytest.mark.asyncio
@pytest.mark.manager
class TestForgotPassword:
    async def test_user_inactive(
        self,
        user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount],
        inactive_user: UserModel,
    ):
        with pytest.raises(UserInactive):
            await user_manager.forgot_password(inactive_user)
        assert user_manager.on_after_forgot_password.called is False

    async def test_user_active(
        self, user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount], user: UserModel
    ):
        await user_manager.forgot_password(user)
        assert user_manager.on_after_forgot_password.called is True

        actual_user = user_manager.on_after_forgot_password.call_args[0][0]
        actual_token = user_manager.on_after_forgot_password.call_args[0][1]

        assert actual_user.id == user.id
        decoded_token = decode_jwt(
            actual_token,
            user_manager.reset_password_token_secret,
            audience=[user_manager.reset_password_token_audience],
        )
        assert decoded_token["sub"] == str(user.id)

        valid_fingerprint, _ = user_manager.password_helper.verify_and_update(
            user.hashed_password, decoded_token["password_fgpt"]
        )
        assert valid_fingerprint is True


@pytest.mark.asyncio
@pytest.mark.manager
class TestResetPassword:
    async def test_invalid_token(
        self, user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount]
    ):
        with pytest.raises(InvalidResetPasswordToken):
            await user_manager.reset_password("foo", "guinevere")
        assert user_manager._update.called is False
        assert user_manager.on_after_reset_password.called is False

    async def test_token_expired(
        self,
        user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount],
        user: UserModel,
        forgot_password_token,
    ):
        with pytest.raises(InvalidResetPasswordToken):
            await user_manager.reset_password(
                forgot_password_token(
                    user.id, current_password_hash=user.hashed_password, lifetime=-1
                ),
                "guinevere",
            )
        assert user_manager._update.called is False
        assert user_manager.on_after_reset_password.called is False

    @pytest.mark.parametrize("user_id", [None, "foo"])
    async def test_valid_token_bad_payload(
        self,
        user_id: str,
        user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount],
        forgot_password_token,
    ):
        with pytest.raises(InvalidResetPasswordToken):
            await user_manager.reset_password(
                forgot_password_token(user_id, current_password_hash="old_password"),
                "guinevere",
            )
        assert user_manager._update.called is False
        assert user_manager.on_after_reset_password.called is False

    async def test_not_existing_user(
        self,
        user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount],
        forgot_password_token,
    ):
        with pytest.raises(UserNotExists):
            await user_manager.reset_password(
                forgot_password_token(
                    "d35d213e-f3d8-4f08-954a-7e0d1bea286f",
                    current_password_hash="old_password",
                ),
                "guinevere",
            )
        assert user_manager._update.called is False
        assert user_manager.on_after_reset_password.called is False

    async def test_already_used_token(
        self,
        user: UserModel,
        user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount],
        forgot_password_token,
    ):
        with pytest.raises(InvalidResetPasswordToken):
            await user_manager.reset_password(
                forgot_password_token(user.id, current_password_hash="old_password"),
                "guinevere",
            )
        assert user_manager._update.called is False
        assert user_manager.on_after_reset_password.called is False

    async def test_inactive_user(
        self,
        inactive_user: UserModel,
        user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount],
        forgot_password_token,
    ):
        with pytest.raises(UserInactive):
            await user_manager.reset_password(
                forgot_password_token(
                    inactive_user.id,
                    current_password_hash=inactive_user.hashed_password,
                ),
                "guinevere",
            )
        assert user_manager._update.called is False
        assert user_manager.on_after_reset_password.called is False

    async def test_invalid_password(
        self,
        user: UserModel,
        user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount],
        forgot_password_token,
    ):
        with pytest.raises(InvalidPasswordException):
            await user_manager.reset_password(
                forgot_password_token(
                    user.id, current_password_hash=user.hashed_password
                ),
                "h",
            )
        assert user_manager.on_after_reset_password.called is False

    async def test_valid_user_password(
        self,
        user: UserModel,
        user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount],
        forgot_password_token,
    ):
        await user_manager.reset_password(
            forgot_password_token(user.id, current_password_hash=user.hashed_password),
            "holygrail",
        )

        assert user_manager._update.called is True
        update_dict = user_manager._update.call_args[0][1]
        assert update_dict == {"password": "holygrail"}

        assert user_manager.on_after_reset_password.called is True
        actual_user = user_manager.on_after_reset_password.call_args[0][0]
        assert actual_user.id == user.id


@pytest.mark.asyncio
@pytest.mark.manager
class TestUpdateUser:
    async def test_safe_update(
        self, user: UserModel, user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount]
    ):
        user_update = schemas.UserUpdate(first_name="Arthur", is_superuser=True)
        updated_user = await user_manager.update(user_update, user, safe=True)

        assert updated_user.first_name == "Arthur"
        assert updated_user.is_superuser is False

        assert user_manager.on_after_update.called is True

    async def test_unsafe_update(
        self, user: UserModel, user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount]
    ):
        user_update = schemas.UserUpdate(first_name="Arthur", is_superuser=True)
        updated_user = await user_manager.update(user_update, user, safe=False)

        assert updated_user.first_name == "Arthur"
        assert updated_user.is_superuser is True

        assert user_manager.on_after_update.called is True

    async def test_password_update_invalid(
        self, user: UserModel, user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount]
    ):
        user_update = schemas.UserUpdate(password="h")
        with pytest.raises(InvalidPasswordException):
            await user_manager.update(user_update, user, safe=True)

        assert user_manager.on_after_update.called is False

    async def test_password_update_valid(
        self, user: UserModel, user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount]
    ):
        old_hashed_password = user.hashed_password
        user_update = schemas.UserUpdate(password="holygrail")
        updated_user = await user_manager.update(user_update, user, safe=True)

        assert updated_user.hashed_password != old_hashed_password

        assert user_manager.on_after_update.called is True

    async def test_email_update_already_existing(
        self,
        user: UserModel,
        superuser: UserModel,
        user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount],
    ):
        user_update = schemas.UserUpdate(email=superuser.email)
        with pytest.raises(UserAlreadyExists):
            await user_manager.update(user_update, user, safe=True)

        assert user_manager.on_after_update.called is False

    async def test_email_update_with_same_email(
        self, user: UserModel, user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount]
    ):
        user_update = schemas.UserUpdate(email=user.email)
        updated_user = await user_manager.update(user_update, user, safe=True)

        assert updated_user.email == user.email

        assert user_manager.on_after_update.called is True


@pytest.mark.asyncio
@pytest.mark.manager
class TestDelete:
    async def test_delete(
        self, user: UserModel, user_manager: UserManagerMock[UserModel, SignInModel, UserOAuth, OAuthAccount]
    ):
        await user_manager.delete(user)

        assert user_manager.on_before_delete.called is True

        assert user_manager.on_after_delete.called is True


def test_integer_id_mixin():
    integer_id_mixin = IntegerIDMixin()

    assert integer_id_mixin.parse_id("123") == 123
    assert integer_id_mixin.parse_id(123) == 123

    with pytest.raises(InvalidID):
        integer_id_mixin.parse_id("123.42")

    with pytest.raises(InvalidID):
        integer_id_mixin.parse_id(123.42)

    with pytest.raises(InvalidID):
        integer_id_mixin.parse_id("abc")
