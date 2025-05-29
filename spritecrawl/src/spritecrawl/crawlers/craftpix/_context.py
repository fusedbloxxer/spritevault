from crawlee.crawlers import PlaywrightCrawlingContext
from dataclasses import dataclass

from ...resources import AssetDatabaseResource, AccountResource, StorageResource
from .._context import WebsiteContext


@dataclass(frozen=True)
class CraftpixWebsiteContext(WebsiteContext):
    database: AssetDatabaseResource
    account: AccountResource
    storage: StorageResource
    login_url: str
    seed_url: str


@dataclass(frozen=True)
class CraftpixCrawlerContext(PlaywrightCrawlingContext, CraftpixWebsiteContext):
    pass
