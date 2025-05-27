import asyncio

from dotenv import load_dotenv

load_dotenv()

from .crawlers import crawlers


async def scrape() -> None:
    for crawler in crawlers:
        await crawler.scrape()


asyncio.run(scrape())
