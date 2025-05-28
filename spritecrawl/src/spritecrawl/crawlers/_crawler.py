from abc import ABC, abstractmethod


class Crawler(ABC):
    def __init__(self, name: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.name = name

    @abstractmethod
    async def scrape(self) -> None:
        raise NotImplementedError()
