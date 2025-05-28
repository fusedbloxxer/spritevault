from dataclasses import dataclass


@dataclass(frozen=True)
class AccountResource:
    username: str
    password: str
