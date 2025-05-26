from crawlee.crawlers import PlaywrightCrawlingContext
from crawlee import Request
import typing as t

from .constants import RouteName
from . import router


@router.default_handler
async def default_handler(context: PlaywrightCrawlingContext) -> None:
    context.log.error(f"Unmatched request found: {context.request.loaded_url}")


@router.handler(RouteName.Category)
async def entry_handler(context: PlaywrightCrawlingContext) -> None:
    context.log.info(f"Category: {context.request.loaded_url}")

    heading_element = context.page.locator("h1", has_text="Pixel Art Sprites")
    await heading_element.wait_for(state="visible")

    article_element = context.page.locator("article[data-item-id] .blog-grid-item > a")
    articles = await article_element.evaluate_all("(e) => e.map(x => x.href)")
    items: t.List[Request] = []

    for article in articles:
        if "freebie" in article:
            items.append(Request.from_url(article, label=RouteName.Freebie))
            continue
        if "product" in article:
            items.append(Request.from_url(article, label=RouteName.Product))
            continue
        context.log.error(f"Unmatched article URL {article}. Will not crawl.")
    await context.add_requests(requests=items)

    next_page_anchor = context.page.locator('a[class="nextpostslink"]').first
    next_page = await next_page_anchor.get_attribute("href")
    if next_page is None:
        return
    await context.add_requests([Request.from_url(next_page, label=RouteName.Category)])



@router.handler(RouteName.Freebie)
async def freebie_handler(context: PlaywrightCrawlingContext) -> None:
    context.log.info(f"Freebie URL: {context.request.loaded_url}")


@router.handler(RouteName.Product)
async def product_handler(context: PlaywrightCrawlingContext) -> None:
    context.log.info(f"Product URL: {context.request.loaded_url}")


# 1. DB to check if asset was already scraped or not. Share connection to DB? Check based on URL only?
# 2. Where to save the scraped data? Use crawlee dataset?
# 3. Authentication for free assets.
# 4. 