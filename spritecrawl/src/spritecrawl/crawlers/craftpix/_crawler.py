from dataclasses import dataclass
from urllib.parse import urlparse
from datetime import timedelta
from typing import Any, cast

from crawlee.crawlers import PlaywrightCrawler
from crawlee.sessions import SessionPool
from crawlee import Request

from ...resources import AssetDatabaseResource, AssetManagerResource, AccountResource
from ...extensions import PlaywrightPageExtension
from .._crawler import Crawler
from ._context import CraftpixWebsiteContext
from ._context import CraftpixCrawlerContext
from ._context import CraftpixStore
from ._common import Labels
from ._routes import router


@dataclass()
class CraftpixResources:
    database: AssetDatabaseResource
    storage: AssetManagerResource
    account: AccountResource


class CraftpixCrawler(Crawler):
    def __init__(self, resources: CraftpixResources) -> None:
        global router

        super().__init__(name="craftpix")

        # Setup crawler context
        self.context = CraftpixWebsiteContext(
            helper=PlaywrightPageExtension[CraftpixCrawlerContext](),
            seed_url="https://craftpix.net/categorys/pixel-art-sprites/",
            login_url="https://craftpix.net/",
            store=CraftpixStore(website_id=0),
            database=resources.database,
            account=resources.account,
            storage=resources.storage,
        )

        # Setup crawler seed
        self.seed = Request.from_url(self.context.login_url, label=Labels.Login)

        # Construct router and notify observers for new contexts
        router.with_context(self.context).with_observer(self.context.helper)
        router = cast(Any, router)

        # Setup crawler settings
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
            request_handler=router,
            session_pool=session,
            headless=True,
        )

    async def scrape(self) -> None:
        async with self.context.database:
            # Insert or Retrieve existing website frm DB
            website = urlparse(self.seed.url).netloc
            website_id = await self.context.database.exi_website(website)

            # Setup dynamic store values
            assert website_id, "Could not obtain website_id!"
            self.context.store.website_id = website_id

            # Start webscraping
            await self.crawler.run([self.seed])
