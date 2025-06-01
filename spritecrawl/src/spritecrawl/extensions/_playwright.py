import os
import uuid

from pathlib import Path
from dataclasses import dataclass
from playwright.async_api import Page
from typing import TypeVar, Generic

from crawlee.crawlers import PlaywrightCrawlingContext

from ..crawlers import RequiresContext


TCC = TypeVar("TCC", bound=PlaywrightCrawlingContext)


@dataclass(frozen=True)
class DownloadOptions:
    dirpath: Path
    filename: str
    url: str


@dataclass
class PlaywrightPageExtension(Generic[TCC], RequiresContext[TCC]):
    page: Page | None = None

    async def download_from_url(self, options: DownloadOptions) -> None:
        assert self.page, "Page does not exist!"

        filename = options.filename
        dirpath = options.dirpath
        url = options.url

        download_func = """
            ([url, name]) => {
                const link = document.createElement("a");
                link.style.display = "none";
                link.download = name;
                link.href = url;

                document.body.appendChild(link);
                link.click();

                setTimeout(() => {
                    URL.revokeObjectURL(link.href);
                    link.parentNode.removeChild(link);
                }, 0);
            }
        """
        async with self.page.expect_download() as download_info:
            await self.page.evaluate(download_func, [url, filename])

        download = await download_info.value
        fileext = os.path.splitext(download.suggested_filename)[1]
        await download.save_as(dirpath / f"{filename}{fileext}")

    async def scroll_to_bottom(self) -> None:
        assert self.page, "Page does not exist!"

        scroll_func = """
            async () => {
                const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

                for (let i = 0; i < document.body.scrollHeight; i += 100) {
                    window.scrollTo(0, i);
                    await delay(100);
                }
            };
        """

        await self.page.evaluate(scroll_func)

    def accept(self, context: PlaywrightCrawlingContext) -> None:
        self.page = context.page
