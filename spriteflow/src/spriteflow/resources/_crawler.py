from pathlib import Path
from dagster import ConfigurableResource, ResourceDependency

from spritecrawl.resources import AccountResource, AssetManagerResource
from spritecrawl.crawlers import CraftpixCrawler, CraftpixResources

from ._database import PostgresAssetDatabaseResource, PostgresConnectionResource


class CrawlerDatabaseResource(ConfigurableResource):
    db_con: PostgresConnectionResource

    def get_database(self) -> PostgresAssetDatabaseResource:
        return PostgresAssetDatabaseResource(self.db_con.dsn)


class CrawlerAccountResource(ConfigurableResource):
    username: str
    password: str


class CrawlerStorageResource(ConfigurableResource):
    path: str


class CraftpixCrawlerResource(ConfigurableResource):
    database: ResourceDependency[CrawlerDatabaseResource]
    storage: ResourceDependency[CrawlerStorageResource]
    account: ResourceDependency[CrawlerAccountResource]
    name: str

    def get_crawler(self) -> CraftpixCrawler:
        account = AccountResource(self.account.username, self.account.password)
        database: PostgresAssetDatabaseResource = self.database.get_database()
        storage = AssetManagerResource(Path(self.storage.path, self.name))
        return CraftpixCrawler(
            CraftpixResources(
                database=database,
                storage=storage,
                account=account,
            ),
        )


__all__ = [
    "CrawlerAccountResource",
    "CrawlerStorageResource",
    "CraftpixCrawlerResource",
    "CrawlerDatabaseResource",
]
