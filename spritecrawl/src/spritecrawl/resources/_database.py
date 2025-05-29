from abc import abstractmethod
from typing import AsyncContextManager, List, Self


class AssetDatabaseResource(AsyncContextManager):
    @abstractmethod
    async def __aenter__(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback) -> Self:
        raise NotImplementedError()

    @abstractmethod
    async def asset_exists(self, asset_id: str) -> bool:
        raise NotImplementedError()

    @abstractmethod
    async def assets_exist(self, asset_ids: List[str]) -> List[bool]:
        raise NotImplementedError()

    @abstractmethod
    async def mark_asset(self, asset_id: str) -> bool:
        raise NotImplementedError()

    @abstractmethod
    async def mark_assets(self, asset_ids: List[str]) -> bool:
        raise NotImplementedError()
