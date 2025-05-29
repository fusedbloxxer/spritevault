from dagster import asset
from dagster import AssetExecutionContext

from .resources import CraftpixCrawlerResource


@asset
async def craftpix_sprites(
    context: AssetExecutionContext, crawler_craftpix: CraftpixCrawlerResource
) -> None:
    """Pixel art spritesheets and metadata from craftpix.net website"""
    context.log.info("Crawling Craftpix")

    # Setup crawler
    crawler = crawler_craftpix.get_crawler()

    # Start scraping
    await crawler.scrape()

