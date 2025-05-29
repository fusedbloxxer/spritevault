import asyncpg

from dataclasses import dataclass
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

        try:
            conn: Connection
            async with self.__pool.acquire() as conn:
                query = "SELECT EXISTS (SELECT 1 FROM assets WHERE asset_id = $1)"
                result = await conn.fetchval(query, asset_id)
                return result is not None
        except Exception as e:
            print(f"Error checking if asset exists: {e}")
            return False

    async def mark_asset(self, asset_id: str) -> bool:
        """
        Marks an asset with the given ID as processed in the database.
        """
        assert self.__pool, "Database connection is closed."

        try:
            conn: Connection
            async with self.__pool.acquire() as conn:
                query = "INSERT INTO assets (asset_id) VALUES ($1)"
                await conn.execute(query, asset_id)
                return True
        except asyncpg.exceptions.UniqueViolationError:
            print(f"Asset with ID {asset_id} already exists in database.")
            return False  # Asset already existed
        except Exception as e:
            print(f"Error marking asset: {e}")
            return False

    async def __aenter__(self) -> None:
        try:
            self.__pool = await asyncpg.create_pool(dsn=self.dsn)
            print("Database connection opened.")
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
