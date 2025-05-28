from crawlee.crawlers import PlaywrightCrawlingContext
from dataclasses import dataclass

from ...resources import DatabaseResource, AccountResource, StorageResource
from .._context import WebsiteContext


@dataclass(frozen=True)
class CraftpixWebsiteContext(WebsiteContext):
    account: AccountResource
    storage: StorageResource
    db: DatabaseResource
    login_url: str
    seed_url: str


@dataclass(frozen=True)
class CraftpixCrawlerContext(PlaywrightCrawlingContext, CraftpixWebsiteContext):
    pass
