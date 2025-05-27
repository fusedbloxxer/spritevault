from crawlee.crawlers import PlaywrightCrawler
from crawlee.sessions import SessionPool
from crawlee import Request

from datetime import timedelta

from ...resources._database import DatabaseWrapper
from ...resources._account import Account

from .._crawler import Crawler

from ._context import CraftpixWebsiteContext
from ._constants import Labels
from ._routes import router


class CraftpixCrawler(Crawler):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Create context
        context = CraftpixWebsiteContext(
            db=DatabaseWrapper(),
            start_url="https://craftpix.net/categorys/pixel-art-sprites/",
        )

        # Setup crawler
        session_settings = {
            "max_age": timedelta(hours=999_999),
            "max_usage_count": 999_999,
            "max_error_score": 100,
        }
        session = SessionPool(
            create_session_settings=session_settings,
            max_pool_size=1,
        )
        self.crawler = PlaywrightCrawler(
            request_handler=router.with_context(context),
            session_pool=session,
            headless=False,
        )

    async def scrape(self) -> None:
        await self.crawler.run(
            [Request.from_url("https://craftpix.net/", label=Labels.Login)],
        )
