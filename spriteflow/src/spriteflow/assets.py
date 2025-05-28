import os

from pathlib import Path
from dagster import asset
from dagster import AssetExecutionContext

from spritecrawl.crawlers import CraftpixCrawler, CraftpixResources, Crawler
from spritecrawl.resources import AccountResource, DatabaseConfig, DatabaseResource, StorageResource


@asset
async def craftpix_sprites(context: AssetExecutionContext) -> None:
    context.log.info("Crawling Craftpix")

    db_username = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    assert db_username and db_password

    craftpix_username = os.getenv('CRAFTPIX_USERNAME')
    craftpix_password = os.getenv('CRAFTPIX_PASSWORD')
    assert craftpix_username and craftpix_password

    scrape_dir = os.getenv('SCRAPE_DIR')
    assert scrape_dir
    craftpix_scrape_dir = Path(scrape_dir, 'craftpix', 'images')

    db_config = DatabaseConfig(f"postgresql://{db_username}:{db_password}@localhost:8092/spritecrawl")
    ac = AccountResource(craftpix_username, craftpix_password)
    storage = StorageResource(storage=craftpix_scrape_dir)
    db = DatabaseResource(db_config)

    crawler: Crawler = CraftpixCrawler(resources=CraftpixResources(database=db, account=ac, storage=storage))
    await crawler.scrape()

