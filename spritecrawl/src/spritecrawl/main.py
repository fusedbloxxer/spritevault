import asyncio
from crawlee import Request


from .crawlers.craftpix.constants import RouteName
from .crawlers.craftpix.crawler import crawler


async def scrape() -> None:
    await crawler.run(
        [
            Request.from_url(
                "https://craftpix.net/categorys/pixel-art-sprites/",
                label=RouteName.Category,
            )
        ]
    )


def main() -> None:
    asyncio.run(scrape())
