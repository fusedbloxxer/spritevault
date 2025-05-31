from crawlee.crawlers import PlaywrightCrawlingContext
from dataclasses import dataclass

from ...resources import AssetDatabaseResource, AccountResource, AssetManagerResource
from .._context import WebsiteContext


@dataclass
class CraftpixStore:
    website_id: int = 0


@dataclass(frozen=True)
class CraftpixWebsiteContext(WebsiteContext):
    database: AssetDatabaseResource
    storage: AssetManagerResource
    account: AccountResource
    store: CraftpixStore
    login_url: str
    seed_url: str


@dataclass(frozen=True)
class CraftpixCrawlerContext(PlaywrightCrawlingContext, CraftpixWebsiteContext):
    pass
