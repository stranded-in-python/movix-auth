from enum import Enum
from typing import Iterable, Union
from uuid import UUID

from pydantic import BaseModel

from db import models_protocol


class ErrorModel(BaseModel):
    detail: Union[str, dict[str, str]]


class ErrorCodeReasonModel(BaseModel):
    code: str
    reason: str


class ErrorCode(str, Enum):
    # Users
    REGISTER_INVALID_PASSWORD = "REGISTER_INVALID_PASSWORD"
    REGISTER_USER_ALREADY_EXISTS = "REGISTER_USER_ALREADY_EXISTS"
    OAUTH_NOT_AVAILABLE_EMAIL = "OAUTH_NOT_AVAILABLE_EMAIL"
    OAUTH_USER_ALREADY_EXISTS = "OAUTH_USER_ALREADY_EXISTS"
    LOGIN_BAD_CREDENTIALS = "LOGIN_BAD_CREDENTIALS"
    LOGIN_USER_NOT_VERIFIED = "LOGIN_USER_NOT_VERIFIED"
    ACCESS_BAD_TOKEN = "ACCESS_BAD_TOKEN"
    REFRESH_BAD_TOKEN = "REFRESH_BAD_TOKEN"
    RESET_PASSWORD_BAD_TOKEN = "RESET_PASSWORD_BAD_TOKEN"
    RESET_PASSWORD_INVALID_PASSWORD = "RESET_PASSWORD_INVALID_PASSWORD"
    VERIFY_USER_BAD_TOKEN = "VERIFY_USER_BAD_TOKEN"
    VERIFY_USER_ALREADY_VERIFIED = "VERIFY_USER_ALREADY_VERIFIED"
    UPDATE_USER_EMAIL_ALREADY_EXISTS = "UPDATE_USER_EMAIL_ALREADY_EXISTS"
    UPDATE_USER_INVALID_PASSWORD = "UPDATE_USER_INVALID_PASSWORD"
    USER_IS_NOT_EXISTS = "USER_IS_NOT_EXISTS"
    USER_HAS_NO_ROLE = "USER_HAS_NO_ROLE"
    USER_HAS_NO_RIGHTS = "USER_HAS_NO_RIGHTS"

    # Roles
    UPDATE_ROLE_NAME_ALREADY_EXISTS = "UPDATE_ROLE_NAME_ALREADY_EXISTS"
    ROLE_IS_NOT_EXISTS = "ROLE_IS_NOT_EXISTS"
    USER_ROLE_IS_EXISTS = "USER_ROLE_IS_EXISTS"
    # Access rights
    UPDATE_ACCESS_NAME_ALREADY_EXISTS = "UPDATE_ACCESS_NAME_ALREADY_EXISTS"
    ACCESS_IS_NOT_EXISTS = "ACCESS_DOES_NOT_EXIST"


async def _get_user_rigths(
    user_id: UUID,
    role_manager,
    access_right_manager,
) -> Iterable[models_protocol.AccessRightProtocol]:
    roles_list = await role_manager.get_user_roles(user_id)
    role_ids = [role.role_id for role in roles_list]
    user_rights = await access_right_manager.get_roles_access_rights(role_ids)

    return user_rights