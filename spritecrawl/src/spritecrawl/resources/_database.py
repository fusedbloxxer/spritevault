from dataclasses import dataclass


@dataclass(frozen=True)
class DatabaseWrapper:
    def exists(self, url: str) -> bool:
        return False
