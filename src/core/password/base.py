from typing import Protocol


class PasswordHelperProtocol(Protocol):
    def verify_and_update(
        self, plain_password: str, hashed_password: str
    ) -> tuple[bool, str]:
        ...

    def hash(self, password: str) -> str:
        ...

    def generate(self) -> str:
        ...
