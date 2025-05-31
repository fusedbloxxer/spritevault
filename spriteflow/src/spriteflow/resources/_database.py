import asyncpg

from dataclasses import dataclass
from dagster import ConfigurableResource
from asyncpg import Pool, Connection, Record
from typing import Self, List, Union, Any, cast

from spritecrawl.resources import AssetDatabaseResource


@dataclass
class PostgresAssetDatabaseResource(AssetDatabaseResource):
    dsn: str

    def __post_init__(self) -> None:
        self.__pool: Pool | None = None

    async def get_website(self, url: str) -> Union[int, None]:
        """Retrieves the website id for the given URL. None if it doesn't exist."""
        assert self.__pool, "Connection pool is empty!"
        con: Connection
        async with self.__pool.acquire() as con:
            try:
                query = """SELECT id FROM website WHERE url = $1"""
                record = await con.fetchrow(query, url)
                return record["id"] if record else None
            except Exception as e:
                print(f"Error getting website: {e}")
                return None

    async def add_website(self, url: str) -> Union[int, None]:
        """Adds a website and returns its id. None if operation failed."""
        assert self.__pool, "Connection pool is empty!"
        con: Connection
        async with self.__pool.acquire() as con:
            try:
                query = """INSERT INTO website (url) VALUES ($1)"""
                await con.execute(query, url)
                record = await self.get_website(url)
                return record
            except Exception as e:
                print(f"Error adding website: {e}")
                return None

    async def exi_website(self, url: str) -> Union[int, None]:
        """Retrieves the website_id for the given URL or creates a new entry."""
        assert self.__pool, "Connection pool is empty!"
        con: Connection
        async with self.__pool.acquire() as con:
            try:
                query = """SELECT id FROM website WHERE url = $1"""
                record = await con.fetchrow(query, url)
                if record:
                    return record["id"]
                query = """INSERT INTO website (url) VALUES ($1)"""
                await con.execute(query, url)
                query = """SELECT id FROM website WHERE url = $1"""
                record = await con.fetchrow(query, url)
                return cast(Record, record)['id']
            except Exception as e:
                print(f"Error ensuring website exists: {e}")
                return None

    async def is_crawled(self, url: str) -> bool:
        """For the given URL checks if it was crawled already. Returns the status for URL."""
        assert self.__pool, "Connection pool is empty!"
        con: Connection
        async with self.__pool.acquire() as con:
            try:
                query = """SELECT EXISTS (SELECT 1 FROM asset_crawl WHERE url = $1)"""
                record = await con.fetchrow(query, url)
                return record[0] if record else False
            except Exception as e:
                print(f"Error checking if crawled: {e}")
                return False

    async def are_crawled(self, urls: List[str]) -> List[bool]:
        """For each given URL checks if it was crawled already. Returns the status for each URL."""
        assert self.__pool, "Connection pool is empty!"
        con: Connection
        async with self.__pool.acquire() as con:
            try:
                query = """SELECT EXISTS (SELECT 1 FROM asset_crawl WHERE url = $1)"""
                args = [(url,) for url in urls]
                records = await con.fetchmany(query, args)
                return [record[0] for record in records]
            except Exception as e:
                print(f"Error checking if crawled: {e}")
                return [False] * len(urls)

    async def mark_asset(self, website_id: int, asset_url: str) -> bool:
        """Marks asset as being crawled. True if operation succeded."""
        assert self.__pool, "Connection pool is empty!"
        con: Connection
        async with self.__pool.acquire() as con:
            try:
                query = """INSERT INTO asset_crawl (url, website_id, is_asset) VALUES ($1, $2, TRUE)"""
                await con.execute(query, asset_url, website_id)
                return True
            except Exception as e:
                print(f"Error marking asset: {e}")
                return False

    async def mark_assets(self, website_id: int, asset_urls: List[str]) -> bool:
        """Marks assets as being crawled. True if operation succeded."""
        assert self.__pool, "Connection pool is empty!"
        con: Connection
        async with self.__pool.acquire() as con:
            try:
                query = """INSERT INTO asset_crawl (url, website_id, is_asset) VALUES ($1, $2, TRUE)"""
                await con.executemany(query, [(url, website_id) for url in asset_urls])
                return True
            except Exception as e:
                print(f"Error marking assets: {e}")
                return False

    async def mark_url(self, website_id: int, url: str) -> bool:
        """Marks URL as being crawled. True if operation succeded."""
        assert self.__pool, "Connection pool is empty!"
        con: Connection
        async with self.__pool.acquire() as con:
            try:
                query = """INSERT INTO asset_crawl (url, website_id) VALUES ($1, $2)"""
                await con.execute(query, url, website_id)
                return True
            except Exception as e:
                print(f"Error marking URL: {e}")
                return False

    async def mark_urls(self, website_id: int, urls: List[str]) -> bool:
        """Marks URLs as being crawled. True if operation succeded."""
        assert self.__pool, "Connection pool is empty!"
        con: Connection
        async with self.__pool.acquire() as con:
            try:
                query = """INSERT INTO asset_crawl (url, website_id) VALUES ($1, $2)"""
                await con.executemany(query, [(url, website_id) for url in urls])
                return True
            except Exception as e:
                print(f"Error marking URLs: {e}")
                return False

    async def __aenter__(self) -> Self:
        try:
            self.__pool = await asyncpg.create_pool(dsn=self.dsn)
            print("Database connection opened.")
            return self
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if self.__pool:
            await self.__pool.close()
            print("Database connection closed.")


class PostgresConnectionResource(ConfigurableResource):
    database: str
    username: str
    password: str
    hostname: str
    port: str

    @property
    def dsn(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.hostname}:{self.port}/{self.database}"


__all__ = [
    "PostgresConnectionResource",
    "PostgresAssetDatabaseResource",
]
