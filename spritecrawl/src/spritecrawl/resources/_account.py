from dataclasses import dataclass


@dataclass(frozen=True)
class Account:
    username: str
    password: str
