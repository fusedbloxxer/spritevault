from crawlee.crawlers import PlaywrightCrawlingContext
from dataclasses import dataclass

from ...resources import AssetDatabaseResource, AssetManagerResource, AccountResource
from ...extensions import PlaywrightPageExtension
from .._context import WebsiteContext


@dataclass
class CraftpixStore:
    website_id: int = 0


@dataclass(frozen=True)
class CraftpixWebsiteContext(WebsiteContext):
    # Extensions with context
    helper: PlaywrightPageExtension

    # Resources
    database: AssetDatabaseResource
    storage: AssetManagerResource
    account: AccountResource

    # Global state store
    store: CraftpixStore

    # Constants
    login_url: str
    seed_url: str


@dataclass(frozen=True)
class CraftpixCrawlerContext(PlaywrightCrawlingContext, CraftpixWebsiteContext):
    pass
