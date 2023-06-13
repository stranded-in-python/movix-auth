import asyncio
import dataclasses
import datetime
import uuid
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Dict,
    Generic,
    Optional,
    Type,
    TypeVar,
    Union,
)
from unittest.mock import MagicMock

import httpx
import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI, Response
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
    username: str | None
    email: EmailStr
    first_name: str | None
    last_name: str | None
    hashed_password: str
    id: IDType = uuid.uuid4()
    is_active: bool = True
    is_superuser: bool = False
    is_admin: bool = False


@dataclasses.dataclass
class SignInModel(models.SignInHistoryEvent[IDType]):
    id: IDType
    user_id: IDType
    timestamp: datetime.datetime
    fingerprint: str


class BaseTestUserManager(
    Generic[models.UP, models.SIHE],
    models.UUIDIDMixin,
    BaseUserManager[models.UP, models.SIHE],
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


class UserManager(BaseTestUserManager[models.UP, models.SIHE]):
    pass


class UserManagerMock(BaseTestUserManager[models.UP, models.SIHE]):
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
    Generic[models.UP, models.SIHE], BaseUserDatabase[models.UP, IDType, models.SIHE]
):
    def __init__(self, user: UserModel, inactive_user: UserModel, superuser: UserModel):
        self.user: UserModel = user
        self.inactive_user: UserModel = inactive_user
        self.superuser: UserModel = superuser

    async def get(self, id: IDType) -> UserModel | None:
        if id == user.id:
            return self.user
        if id == inactive_user.id:
            return self.inactive_user
        if id == superuser.id:
            return self.superuser
        return None

    async def get_by_email(self, email: str) -> Optional[UserModel]:
        lower_email = email.lower()
        if lower_email == user.email.lower():
            return self.user
        if lower_email == inactive_user.email.lower():
            return self.inactive_user
        if lower_email == superuser.email.lower():
            return self.superuser
        return None

    async def create(self, create_dict: Dict[str, Any]) -> UserModel:
        return UserModel(**create_dict)

    async def update(self, user: UserModel, update_dict: Dict[str, Any]) -> UserModel:
        for field, value in update_dict.items():
            setattr(user, field, value)
        return user

    async def delete(self, user: UserModel) -> None:  # pyright: ignore
        pass


@pytest.fixture
def mock_user_db(
    user: UserModel, inactive_user: UserModel, superuser: UserModel
) -> BaseUserDatabase[UserModel, IDType, SignInModel]:
    return MockUserDatabase[UserModel, SignInModel](user, inactive_user, superuser)


@pytest.fixture
def make_user_manager(mocker: MockerFixture):
    def _make_user_manager(user_manager_class: Type[BaseTestUserManager], mock_user_db):
        user_manager = user_manager_class(mock_user_db)
        mocker.spy(user_manager, "get_by_email")
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
    def __init__(self, tokenUrl: str):
        super().__init__(tokenUrl)

    async def get_logout_response(self) -> Any:
        return Response()

    @staticmethod
    def get_openapi_logout_responses_success() -> OpenAPIResponseType:
        return {}


class MockStrategy(Strategy[UserModel, SignInModel]):
    async def read_token(
        self,
        token: Optional[str],
        user_manager: BaseUserManager[UserModel, SignInModel],
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
        transport=MockTransport(tokenUrl="/login"),
        get_strategy=lambda: MockStrategy(),
    )


@pytest.fixture
def mock_authentication():
    return get_mock_authentication(name="mock")


@pytest.fixture
def get_test_client():
    async def _get_test_client(app: FastAPI) -> AsyncGenerator[httpx.AsyncClient, None]:
        async with LifespanManager(app):
            async with httpx.AsyncClient(
                app=app, base_url="http://app.io"
            ) as test_client:
                yield test_client

    return _get_test_client
