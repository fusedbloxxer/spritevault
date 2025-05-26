from crawlee.crawlers import PlaywrightCrawler

from .routes import router

crawler = PlaywrightCrawler(
    max_requests_per_crawl=10,
    request_handler=router,
    headless=False,
)
