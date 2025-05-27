from crawlee.crawlers import PlaywrightCrawlingContext
from dataclasses import dataclass

from ...resources._database import DatabaseWrapper
from ...resources._account import Account
from .._context import WebsiteContext


@dataclass(frozen=True)
class CraftpixWebsiteContext(WebsiteContext):
    db: DatabaseWrapper
    account: Account
    start_url: str


@dataclass(frozen=True)
class CraftpixContext(PlaywrightCrawlingContext, CraftpixWebsiteContext):
    pass
