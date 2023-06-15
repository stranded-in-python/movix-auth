import asyncio
import dataclasses
import datetime
import uuid
from typing import Any, AsyncGenerator, Callable, Dict, Generic, Optional, Type, Union
from unittest.mock import MagicMock

import httpx
import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI, Response
from httpx_oauth.oauth2 import OAuth2
from pydantic import EmailStr, SecretStr
from pytest_mock import MockerFixture

from api import schemas
from authentication import AuthenticationBackend, BearerTransport
from authentication.strategy import Strategy
from authentication.strategy.jwt import SecretType
from core import exceptions
from core.password.password import PasswordHelper
from db import models_protocol as models
from db.base import BaseUserDatabase
from managers.user import BaseUserManager
from openapi import OpenAPIResponseType

password_helper = PasswordHelper()
guinevere_password_hash = password_helper.hash("guinevere")
angharad_password_hash = password_helper.hash("angharad")
viviane_password_hash = password_helper.hash("viviane")
lancelot_password_hash = password_helper.hash("lancelot")
excalibur_password_hash = password_helper.hash("excalibur")


IDType = uuid.UUID


@dataclasses.dataclass
class UserModel:
    email: EmailStr
    hashed_password: str
    id: IDType = dataclasses.field(default_factory=uuid.uuid4)
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False
    is_admin: bool = False


@dataclasses.dataclass
class OAuthAccount:
    oauth_name: str
    access_token: str
    account_id: str
    account_email: str
    id: uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)
    expires_at: Optional[int] = None
    refresh_token: Optional[str] = None


@dataclasses.dataclass
class UserOAuth:
    oauth_accounts: list[OAuthAccount]
    email: EmailStr
    hashed_password: str
    id: IDType = dataclasses.field(default_factory=uuid.uuid4)
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False
    is_admin: bool = False


@dataclasses.dataclass
class SignInModel(models.SignInHistoryEvent[IDType]):
    id: IDType
    user_id: IDType
    timestamp: datetime.datetime
    fingerprint: str


class User(schemas.BaseUser[IDType]):
    first_name: Optional[str]


class BaseTestUserManager(
    Generic[models.UP, models.SIHE, models.OAP, models.UOAP],
    models.UUIDIDMixin,
    BaseUserManager[models.UP, models.SIHE, models.OAP, models.UOAP],
):
    reset_password_token_secret = "SECRET"  # type: ignore
    verification_token_secret = "SECRET"  # type: ignore

    async def validate_password(
        self, password: str, user: Union[schemas.UC, models.UP]
    ) -> None:
        if len(password) < 3:
            raise exceptions.InvalidPasswordException(
                reason="Password should be at least 3 characters"
            )


class UserManager(BaseTestUserManager[models.UP, models.SIHE, models.OAP, models.UOAP]):
    pass


class UserManagerOAuth(
    BaseTestUserManager[models.UP, models.SIHE, models.OAP, models.UOAP]
):
    pass


class UserManagerMock(
    BaseTestUserManager[models.UP, models.SIHE, models.OAP, models.UOAP]
):
    get_by_email: MagicMock
    forgot_password: MagicMock
    reset_password: MagicMock
    on_after_register: MagicMock
    on_after_forgot_password: MagicMock
    on_after_reset_password: MagicMock
    on_after_update: MagicMock
    on_before_delete: MagicMock
    on_after_delete: MagicMock
    on_after_login: MagicMock
    _update: MagicMock


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


AsyncMethodMocker = Callable[..., MagicMock]


@pytest.fixture
def async_method_mocker(mocker: MockerFixture) -> AsyncMethodMocker:
    def _async_method_mocker(
        object: Any, method: str, return_value: Any = None
    ) -> MagicMock:
        mock: MagicMock = mocker.MagicMock()

        future: asyncio.Future = asyncio.Future()
        future.set_result(return_value)
        mock.return_value = future
        mock.side_effect = None

        setattr(object, method, mock)

        return mock

    return _async_method_mocker


@pytest.fixture(params=["SECRET", SecretStr("SECRET")])
def secret(request) -> SecretType:
    return request.param


@pytest.fixture
def user() -> UserModel:
    return UserModel(
        email=EmailStr("king.arthur@camelot.bt"),
        hashed_password=guinevere_password_hash,
        username='king.arthur',
        first_name='arthur',
        last_name='king',
    )


@pytest.fixture
def user_oauth(oauth_account1: OAuthAccount, oauth_account2: OAuthAccount) -> UserOAuth:
    return UserOAuth(
        email="king.arthur@camelot.bt",
        hashed_password=guinevere_password_hash,
        oauth_accounts=[oauth_account1, oauth_account2],
    )


@pytest.fixture
def inactive_user_oauth(oauth_account3: OAuthAccount) -> UserOAuth:
    return UserOAuth(
        email="percival@camelot.bt",
        hashed_password=angharad_password_hash,
        is_active=False,
        oauth_accounts=[oauth_account3],
    )


@pytest.fixture
def superuser_oauth() -> UserOAuth:
    return UserOAuth(
        email="merlin@camelot.bt",
        hashed_password=viviane_password_hash,
        is_superuser=True,
        oauth_accounts=[],
    )


@pytest.fixture
def oauth_account1() -> OAuthAccount:
    return OAuthAccount(
        oauth_name="service1",
        access_token="TOKEN",
        expires_at=1579000751,
        account_id="user_oauth1",
        account_email="king.arthur@camelot.bt",
    )


@pytest.fixture
def oauth_account2() -> OAuthAccount:
    return OAuthAccount(
        oauth_name="service2",
        access_token="TOKEN",
        expires_at=1579000751,
        account_id="user_oauth2",
        account_email="king.arthur@camelot.bt",
    )


@pytest.fixture
def oauth_account3() -> OAuthAccount:
    return OAuthAccount(
        oauth_name="service3",
        access_token="TOKEN",
        expires_at=1579000751,
        account_id="inactive_user_oauth1",
        account_email="percival@camelot.bt",
    )


@pytest.fixture
def oauth_account4() -> OAuthAccount:
    return OAuthAccount(
        oauth_name="service4",
        access_token="TOKEN",
        expires_at=1579000751,
        account_id="verified_user_oauth1",
        account_email="lake.lady@camelot.bt",
    )


@pytest.fixture
def oauth_account5() -> OAuthAccount:
    return OAuthAccount(
        oauth_name="service5",
        access_token="TOKEN",
        expires_at=1579000751,
        account_id="verified_superuser_oauth1",
        account_email="the.real.merlin@camelot.bt",
    )


@pytest.fixture
def inactive_user() -> UserModel:
    return UserModel(
        email=EmailStr("percival@camelot.bt"),
        hashed_password=angharad_password_hash,
        username='percy',
        first_name='sir',
        last_name='percival',
        is_active=False,
    )


@pytest.fixture
def superuser() -> UserModel:
    return UserModel(
        email=EmailStr("merlin@camelot.bt"),
        hashed_password=viviane_password_hash,
        username='merlin',
        first_name='merlin',
        last_name='the_great',
        is_superuser=True,
    )


class MockUserDatabase(
    Generic[models.UP, models.SIHE, models.OAP, models.UOAP],
    BaseUserDatabase[models.UP, IDType, models.SIHE, models.OAP, models.UOAP],
):
    def __init__(self, user: UserModel, inactive_user: UserModel, superuser: UserModel):
        self.user: UserModel = user
        self.inactive_user: UserModel = inactive_user
        self.superuser: UserModel = superuser

    async def get(self, user_id: IDType) -> UserModel | None:
        if user_id == self.user.id:
            return self.user
        if user_id == self.inactive_user.id:
            return self.inactive_user
        if user_id == self.superuser.id:
            return self.superuser
        return None

    async def get_by_email(self, email: str) -> Optional[UserModel]:
        lower_email = email.lower()
        if lower_email == self.user.email.lower():
            return self.user
        if lower_email == self.inactive_user.email.lower():
            return self.inactive_user
        if lower_email == self.superuser.email.lower():
            return self.superuser
        return None

    async def get_by_username(self, username: str) -> Optional[UserModel]:
        lower_username = username.lower()
        if self.user.username and lower_username == self.user.username.lower():
            return self.user
        if (
            self.inactive_user.username
            and lower_username == self.inactive_user.username.lower()
        ):
            return self.inactive_user
        if (
            self.superuser.username
            and lower_username == self.superuser.username.lower()
        ):
            return self.superuser

        return None

    async def create(self, create_dict: dict[str, Any]) -> UserModel:
        return UserModel(**create_dict)

    async def update(self, user: UserModel, update_dict: dict[str, Any]) -> UserModel:
        for field, value in update_dict.items():
            setattr(user, field, value)
        return user

    async def delete(self, user: UserModel) -> None:  # pyright: ignore
        pass


@pytest.fixture
def mock_user_db(
    user: UserModel, inactive_user: UserModel, superuser: UserModel
) -> BaseUserDatabase[UserModel, IDType, SignInModel, UserOAuth, OAuthAccount]:
    return MockUserDatabase[UserModel, SignInModel, UserOAuth, OAuthAccount](
        user, inactive_user, superuser
    )


@pytest.fixture
def make_user_manager(mocker: MockerFixture):
    def _make_user_manager(user_manager_class: type[BaseTestUserManager], mock_user_db):
        user_manager = user_manager_class(mock_user_db)
        mocker.spy(user_manager, "get_by_email")
        mocker.spy(user_manager, "get_by_username")
        mocker.spy(user_manager, "forgot_password")
        mocker.spy(user_manager, "reset_password")
        mocker.spy(user_manager, "on_after_register")
        mocker.spy(user_manager, "on_after_forgot_password")
        mocker.spy(user_manager, "on_after_reset_password")
        mocker.spy(user_manager, "on_after_update")
        mocker.spy(user_manager, "on_before_delete")
        mocker.spy(user_manager, "on_after_delete")
        mocker.spy(user_manager, "on_after_login")
        mocker.spy(user_manager, "_update")
        return user_manager

    return _make_user_manager


@pytest.fixture
def user_manager(make_user_manager, mock_user_db):
    return make_user_manager(UserManager, mock_user_db)


@pytest.fixture
def get_user_manager(user_manager):
    def _get_user_manager():
        return user_manager

    return _get_user_manager


class MockTransport(BearerTransport):
    def __init__(self, token_url: str):
        super().__init__(token_url)

    async def get_logout_response(self) -> Any:
        return Response()

    @staticmethod
    def get_openapi_logout_responses_success() -> OpenAPIResponseType:
        return {}


class MockStrategy(Strategy[UserModel, SignInModel]):
    async def read_token(
        self,
        token: Optional[str],
        user_manager: BaseUserManager[UserModel, SignInModel, UserOAuth, OAuthAccount],
    ) -> Optional[UserModel]:
        if token is not None:
            try:
                parsed_id = user_manager.parse_id(token)
                return await user_manager.get(parsed_id)
            except (exceptions.InvalidID, exceptions.UserNotExists):
                return None
        return None

    async def write_token(self, user: UserModel) -> str:
        return str(user.id)

    async def destroy_token(self, token: str, user: UserModel) -> None:
        return None


def get_mock_authentication(name: str):
    return AuthenticationBackend(
        name=name,
        transport=MockTransport(token_url="api/v1/login"),
        get_strategy=lambda: MockStrategy(),
    )


@pytest.fixture
def mock_authentication():
    return get_mock_authentication(name="mock")


@pytest.fixture
def refresh_mock_authentication():
    return get_mock_authentication(name="refresh_mock")


@pytest.fixture
def get_test_client():
    async def _get_test_client(app: FastAPI) -> AsyncGenerator[httpx.AsyncClient, None]:
        async with LifespanManager(app):
            async with httpx.AsyncClient(
                app=app, base_url="http://app.io"
            ) as test_client:
                yield test_client

    return _get_test_client


@pytest.fixture
def mock_user_db_oauth(
    user_oauth: UserOAuth, inactive_user_oauth: UserOAuth, superuser_oauth: UserOAuth
) -> BaseUserDatabase[UserModel, IDType, SignInModel, UserOAuth, OAuthAccount]:
    class MockUserDatabase(
        BaseUserDatabase[UserModel, IDType, SignInModel, UserOAuth, OAuthAccount]
    ):
        async def get(self, id: IDType) -> Optional[UserOAuth]:
            if id == user_oauth.id:
                return user_oauth
            if id == inactive_user_oauth.id:
                return inactive_user_oauth
            if id == superuser_oauth.id:
                return superuser_oauth
            return None

        async def get_by_email(self, email: str) -> Optional[UserOAuth]:
            lower_email = email.lower()
            if lower_email == user_oauth.email.lower():
                return user_oauth
            if lower_email == inactive_user_oauth.email.lower():
                return inactive_user_oauth
            if lower_email == superuser_oauth.email.lower():
                return superuser_oauth
            return None

        async def get_by_oauth_account(
            self, oauth: str, account_id: str
        ) -> Optional[UserOAuth]:
            user_oauth_account = user_oauth.oauth_accounts[0]
            if (
                user_oauth_account.oauth_name == oauth
                and user_oauth_account.account_id == account_id
            ):
                return user_oauth

            inactive_user_oauth_account = inactive_user_oauth.oauth_accounts[0]
            if (
                inactive_user_oauth_account.oauth_name == oauth
                and inactive_user_oauth_account.account_id == account_id
            ):
                return inactive_user_oauth
            return None

        async def create(self, create_dict: dict[str, Any]) -> UserOAuth:
            return UserOAuth(**create_dict)

        async def update(
            self, user: UserOAuth, update_dict: dict[str, Any]
        ) -> UserOAuth:
            for field, value in update_dict.items():
                setattr(user, field, value)
            return user

        async def delete(self, user: UserOAuth) -> None:
            pass

        async def add_oauth_account(
            self, user: UserOAuth, create_dict: dict[str, Any]
        ) -> UserOAuth:
            oauth_account = OAuthAccount(**create_dict)
            user.oauth_accounts.append(oauth_account)
            return user

        async def update_oauth_account(  # type: ignore
            self,
            user: UserOAuth,
            oauth_account: OAuthAccount,
            update_dict: dict[str, Any],
        ) -> UserOAuth:
            for field, value in update_dict.items():
                setattr(oauth_account, field, value)
            updated_oauth_accounts = []
            for existing_oauth_account in user.oauth_accounts:
                if (
                    existing_oauth_account.account_id == oauth_account.account_id
                    and existing_oauth_account.oauth_name == oauth_account.oauth_name
                ):
                    updated_oauth_accounts.append(oauth_account)
                else:
                    updated_oauth_accounts.append(existing_oauth_account)
            return user

    return MockUserDatabase()


@pytest.fixture
def user_manager_oauth(make_user_manager, mock_user_db_oauth):
    return make_user_manager(UserManagerOAuth, mock_user_db_oauth)


@pytest.fixture
def get_user_manager_oauth(user_manager_oauth):
    def _get_user_manager_oauth():
        return user_manager_oauth

    return _get_user_manager_oauth


@pytest.fixture
def oauth_client() -> OAuth2:
    CLIENT_ID = "CLIENT_ID"
    CLIENT_SECRET = "CLIENT_SECRET"
    AUTHORIZE_ENDPOINT = "https://www.camelot.bt/authorize"
    ACCESS_TOKEN_ENDPOINT = "https://www.camelot.bt/access-token"

    return OAuth2(
        CLIENT_ID,
        CLIENT_SECRET,
        AUTHORIZE_ENDPOINT,
        ACCESS_TOKEN_ENDPOINT,
        name="service1",
    )
