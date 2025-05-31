from abc import abstractmethod
from typing import AsyncContextManager, Union, List, Self


class AssetDatabaseResource(AsyncContextManager):
    @abstractmethod
    async def __aenter__(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback) -> Self:
        raise NotImplementedError()

    @abstractmethod
    async def get_website(self, url: str) -> Union[int, None]:
        """Retrieves the website id for the given URL. None if it doesn't exist."""
        raise NotImplementedError()

    @abstractmethod
    async def add_website(self, url: str) -> Union[int, None]:
        """Adds a website and returns its id. None if operation failed."""
        raise NotImplementedError()

    @abstractmethod
    async def exi_website(self, url: str) -> Union[int, None]:
        """Retrieves the website_id for the given URL or creates a new entry."""
        raise NotImplementedError()

    @abstractmethod
    async def is_crawled(self, url: str) -> bool:
        """For the given URL checks if it was crawled already. Returns the status for URL."""
        raise NotImplementedError()

    @abstractmethod
    async def are_crawled(self, urls: List[str]) -> List[bool]:
        """For each given URL checks if it was crawled already. Returns the status for each URL."""
        raise NotImplementedError()

    @abstractmethod
    async def mark_asset(self, website_id: int, asset_url: str) -> bool:
        """Marks asset as being cralwed. True if operation succeded."""
        raise NotImplementedError()

    @abstractmethod
    async def mark_assets(self, website_id: int, asset_urls: List[str]) -> bool:
        """Marks assets as being crawled. True if operation succeded."""
        raise NotImplementedError()

    @abstractmethod
    async def mark_url(self, website_id: int, url: str) -> bool:
        """Marks URL as being crawled. True if operation succeded."""
        raise NotImplementedError()

    @abstractmethod
    async def mark_urls(self, website_id: int, urls: List[str]) -> bool:
        """Marks URLs as being crawled. True if operation succeded."""
        raise NotImplementedError()
