import os

from typing import cast
from dagster import EnvVar

from ._database import PostgresConnectionResource
from ._crawler import CrawlerAccountResource, CrawlerStorageResource
from ._crawler import CraftpixCrawlerResource, CrawlerDatabaseResource


db_con = PostgresConnectionResource(
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
crawler_database = CrawlerDatabaseResource(
    db_con=db_con,
)
crawler_craftpix = CraftpixCrawlerResource(
    storage=crawler_craftpix_storage,
    account=crawler_craftpix_account,
    database=crawler_database,
)

all_resources = {
    "crawler_craftpix": crawler_craftpix,
}

__all__ = ["all_resources"]
