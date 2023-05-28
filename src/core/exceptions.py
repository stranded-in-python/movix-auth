from typing import Any


class AppException(Exception):
    pass


class InvalidID(AppException):
    pass


class UserAlreadyExists(AppException):
    pass


class UserNotExists(AppException):
    pass


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
