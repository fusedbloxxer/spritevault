import asyncpg

from dataclasses import dataclass
from typing import Self, List, cast
from asyncpg import Pool, Connection
from dagster import ConfigurableResource

from spritecrawl.resources import AssetDatabaseResource


@dataclass
class PostgresAssetDatabaseResource(AssetDatabaseResource):
    dsn: str

    def __post_init__(self) -> None:
        self.__pool: Pool | None = None

    async def asset_exists(self, asset_id: str) -> bool:
        """
        Checks if an asset with the given ID already exists in the database.
        """
        assert self.__pool, "Database connection is closed."
        result: List[bool] = await self.assets_exist([asset_id])
        return False if len(result) == 0 else result[0]

    async def assets_exist(self, asset_ids: List[str]) -> List[bool]:
        """
        Checks which assets from the input list already exist in the database using a batched query.
        Returns a list of boolean for each asset.
        """
        assert self.__pool, "Database connection is closed."
        try:
            conn: Connection
            async with self.__pool.acquire() as conn:
                assets = list(map(lambda x: (x,), asset_ids))
                query = """SELECT EXISTS (SELECT 1 FROM asset_crawl WHERE asset_key = $1);"""
                rows = await conn.fetchmany(query, assets)
                rows = [column[0] for column in rows]
                return cast(List[bool], rows)
        except Exception as e:
            print(f"Error checking if assets exist: {e}")
            return []

    async def mark_asset(self, asset_id: str) -> bool:
        """
        Marks an asset with the given ID as processed in the database.
        """
        assert self.__pool, "Database connection is closed."
        return await self.mark_assets([asset_id])

    async def mark_assets(self, asset_ids: List[str]) -> bool:
        """
        Marks asset with the given IDs as processed in the database.
        """
        assert self.__pool, "Database connection is closed."
        try:
            conn: Connection
            async with self.__pool.acquire() as conn:
                assets = list(map(lambda x: (x,), asset_ids))
                query = """INSERT INTO asset_crawl (asset_key) VALUES ($1)"""
                await conn.executemany(query, assets)
                return True
        except Exception as e:
            print(f"Error marking assets: {e}")
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
