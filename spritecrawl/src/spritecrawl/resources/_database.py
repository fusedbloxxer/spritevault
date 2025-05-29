import asyncpg

from asyncpg import Pool
from dataclasses import dataclass


@dataclass(frozen=True)
class DatabaseConfig:
    dsn: str


@dataclass()
class DatabaseResource:
    config: DatabaseConfig

    def __post_init__(self):
        self.__pool: Pool | None = None

    async def connect(self) -> None:
        try:
            self.__pool = await asyncpg.create_pool(dsn=self.config.dsn)
            print("Database connection opened.")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise

    async def close(self) -> None:
        if self.__pool:
            await self.__pool.close()
            print("Database connection closed.")

    async def url_exists(self, url: str) -> bool:
        assert self.__pool, "Not connected to database!"
        try:
            async with self.__pool.acquire() as conn:
                query = "SELECT EXISTS (SELECT 1 FROM files WHERE url = $1)"
                result = await conn.fetchval(query, url)
                return result
        except Exception as e:
            print(f"Database error checking URL {url}: {e}")
            return False

    async def __aenter__(self) -> None:
        await self.connect()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
