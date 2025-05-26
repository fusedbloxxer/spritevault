import asyncio

from .crawlers.craftpix.crawler import crawler


async def scrape() -> None:
    await crawler.run(["https://craftpix.net/categorys/pixel-art-sprites/"])


def main() -> None:
    asyncio.run(scrape())
