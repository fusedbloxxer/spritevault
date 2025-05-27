from typing import Protocol


class Crawler(Protocol):
    async def scrape(self) -> None:
        pass
