from typing import Any


class AppException(Exception):
    pass


class AccessRightAlreadyExists(AppException):
    pass


class AccessRightNotExists(AppException):
    pass


class ChannelNotExists(AppException):
    pass


class InvalidID(AppException):
    pass


class UserAlreadyExists(AppException):
    pass


class UserNotExists(AppException):
    pass


class UserHasNoRights(AppException):
    ...


class UserInactive(AppException):
    pass


class UserAlreadyVerified(AppException):
    pass


class InvalidVerifyToken(AppException):
    pass


class InvalidResetPasswordToken(AppException):
    pass


class InvalidPasswordException(AppException):
    def __init__(self, reason: Any) -> None:
        self.reason = reason


class RoleNotExists(AppException):
    pass


class RoleAlreadyExists(AppException):
    pass


class UserHaveNotRole(AppException):
    pass


class RoleAlreadyAssign(AppException):
    pass


class RoleHaveNotAccessRight(AppException):
    pass


class AccessRightAlreadyAssign(AppException):
    pass


class TokenInBlacklist(AppException):
    pass


class UserHasNoRight(AppException):
    pass


class UserHasNoRole(AppException):
    pass
