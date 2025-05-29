from abc import abstractmethod
from typing import AsyncContextManager


class AssetDatabaseResource(AsyncContextManager):
    @abstractmethod
    async def __aenter__(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def asset_exists(self, asset_url: str) -> bool:
        raise NotImplementedError()

    @abstractmethod
    async def mark_asset(self, asset_url: str) -> bool:
        raise NotImplementedError()
