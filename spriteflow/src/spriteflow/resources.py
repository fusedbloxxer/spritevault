import os

from typing import cast
from pathlib import Path
from dagster import EnvVar
from dagster import ConfigurableResource, ResourceDependency

from spritecrawl.crawlers import CraftpixCrawler, CraftpixResources
from spritecrawl.resources import DatabaseConfig, DatabaseResource
from spritecrawl.resources import AccountResource, StorageResource


class PostgresConnectionResource(ConfigurableResource):
    database: str
    username: str
    password: str
    hostname: str
    port: str

    @property
    def dsn(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.hostname}:{self.port}/{self.database}"


class CrawlerDatabaseResource(ConfigurableResource):
    connection: ResourceDependency[PostgresConnectionResource]


class CrawlerAccountResource(ConfigurableResource):
    username: str
    password: str


class CrawlerStorageResource(ConfigurableResource):
    path: str


class CraftpixCrawlerResource(ConfigurableResource):
    database: ResourceDependency[CrawlerDatabaseResource]
    storage: ResourceDependency[CrawlerStorageResource]
    account: ResourceDependency[CrawlerAccountResource]

    def get_crawler(self) -> CraftpixCrawler:
        account = AccountResource(self.account.username, self.account.password)
        db_config = DatabaseConfig(dsn=self.database.connection.dsn)
        storage = StorageResource(Path(self.storage.path))
        db_resource = DatabaseResource(config=db_config)
        return CraftpixCrawler(
            CraftpixResources(
                database=db_resource,
                storage=storage,
                account=account,
            ),
        )


db_connection = PostgresConnectionResource(
    password=EnvVar("POSTGRES_PASSWORD"),
    username=EnvVar("POSTGRES_USER"),
    database=EnvVar("POSTGRES_DB"),
    hostname="localhost",
    port="8092",
)

crawler_craftpix_storage = CrawlerStorageResource(
    path=os.path.join(cast(str, EnvVar("SCRAPE_DIR").get_value()), "craftpix", "images")
)
crawler_craftpix_account = CrawlerAccountResource(
    username=EnvVar("CRAFTPIX_USERNAME"), password=EnvVar("CRAFTPIX_PASSWORD")
)
crawler_craftpix_database = CrawlerDatabaseResource(
    connection=db_connection,
)
crawler_craftpix = CraftpixCrawlerResource(
    database=crawler_craftpix_database,
    storage=crawler_craftpix_storage,
    account=crawler_craftpix_account,
)

all_resources = {
    "crawler_craftpix": crawler_craftpix,
}

__all__ = ["PostgresConnectionResource", "CraftpixCrawlerResource", "all_resources"]
