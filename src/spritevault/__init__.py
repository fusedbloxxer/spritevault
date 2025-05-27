import asyncio

from spritecrawl import crawlers


async def scrape() -> None:
    for crawler in crawlers:
        await crawler.scrape()


def main() -> None:
    asyncio.run(scrape())
