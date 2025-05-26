from crawlee.crawlers import PlaywrightCrawlingContext

from . import router


@router.default_handler
async def default_handler(context: PlaywrightCrawlingContext) -> None:
    context.log.info("default handler")
    await context.page.locator("h1", has_text="Pixel Art Sprites").wait_for(state="hidden")
    context.log.info("page loaded")