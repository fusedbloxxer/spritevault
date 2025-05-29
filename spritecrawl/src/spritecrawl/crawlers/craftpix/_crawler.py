from crawlee.crawlers import PlaywrightCrawler
from crawlee.sessions import SessionPool
from crawlee import Request

from dataclasses import dataclass
from datetime import timedelta

from ...resources import AssetDatabaseResource, AccountResource, StorageResource
from .._crawler import Crawler
from ._context import CraftpixWebsiteContext
from ._common import Labels
from ._routes import router


@dataclass()
class CraftpixResources:
    database: AssetDatabaseResource
    storage: StorageResource
    account: AccountResource


class CraftpixCrawler(Crawler):
    def __init__(self, resources: CraftpixResources) -> None:
        super().__init__(name="craftpix")

        # Setup crawler context
        self.context = CraftpixWebsiteContext(
            seed_url="https://craftpix.net/categorys/pixel-art-sprites/",
            login_url="https://craftpix.net/",
            database=resources.database,
            account=resources.account,
            storage=resources.storage,
        )

        # Setup crawler seed
        self.seed = Request.from_url(self.context.login_url, label=Labels.Login)

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
            request_handler=router.with_context(self.context),
            session_pool=session,
            headless=False,
        )

    async def scrape(self) -> None:
        async with self.context.database:
            await self.crawler.run([self.seed])
