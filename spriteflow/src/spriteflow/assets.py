from dagster import asset
from dagster import AssetExecutionContext

from .resources import CraftpixCrawlerResource
from spritecrawl.crawlers import CraftpixCrawler


@asset
async def craftpix_sprites(
    context: AssetExecutionContext, crawler_craftpix: CraftpixCrawlerResource
) -> None:
    """Pixel art spritesheets and metadata from craftpix.net website"""
    context.log.info("Crawling Craftpix")

    # Setup crawler
    crawler: CraftpixCrawler = crawler_craftpix.get_crawler()

    # debug
    await crawler.scrape()
