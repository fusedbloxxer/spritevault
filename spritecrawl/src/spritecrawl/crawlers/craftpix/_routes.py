import typing as t

from crawlee import Request
from pathlib import Path

from .._router import RouterWithContext
from ._context import CraftpixWebsiteContext
from ._context import CraftpixCrawlerContext
from ._common import Labels


router = RouterWithContext[CraftpixCrawlerContext, CraftpixWebsiteContext]()


@router.default_handler
async def default_handler(context: CraftpixCrawlerContext) -> None:
    raise RuntimeError(f"Unmatched request found: {context.request.loaded_url}")


@router.handler(Labels.Login)
async def login_handler(context: CraftpixCrawlerContext) -> None:
    login_element = context.page.locator("a.lr-singin")
    await login_element.click()

    auth_form = context.page.locator("#auth-form")
    await auth_form.wait_for(state="visible")

    await auth_form.locator("#user_login").type(context.account.username, delay=25)
    await auth_form.locator("#user_pass").type(context.account.password, delay=25)
    await auth_form.locator("#submit-btn").click()

    account_element = context.page.locator('a > i[class="icon-account"]')
    await account_element.wait_for(state="visible")
    await context.page.wait_for_timeout(2000)

    await context.add_requests(
        [Request.from_url(context.seed_url, label=Labels.Category)]
    )


@router.handler(Labels.Category)
async def category_handler(context: CraftpixCrawlerContext) -> None:
    context.log.info(f"Category: {context.request.loaded_url}")

    heading_element = context.page.locator("h1", has_text="Pixel Art Sprites")
    await heading_element.wait_for(state="visible")

    article_element = context.page.locator("article[data-item-id] .blog-grid-item > a")
    articles = await article_element.evaluate_all("(e) => e.map(x => x.href)")
    items: t.List[Request] = []

    for article in articles:
        if "freebie" in article:
            items.append(Request.from_url(article, label=Labels.Freebie))
            continue
        if "product" in article:
            items.append(Request.from_url(article, label=Labels.Product))
            continue
        context.log.error(f"Unmatched article URL {article}. Will not crawl.")
    await context.add_requests(requests=items)

    next_page_anchor = context.page.locator('a[class="nextpostslink"]').first
    next_page = await next_page_anchor.get_attribute("href")
    if next_page is None:
        return
    await context.add_requests([Request.from_url(next_page, label=Labels.Category)])


@router.handler(Labels.Freebie)
async def freebie_handler(context: CraftpixCrawlerContext) -> None:
    context.log.info(f"Freebie URL: {context.request.loaded_url}")

    download_button = context.page.locator("a.gtm-download-free").first
    link = await download_button.get_attribute("href")
    assert link

    await context.add_requests([Request.from_url(link, label=Labels.Download)])


@router.handler(Labels.Product)
async def product_handler(context: CraftpixCrawlerContext) -> None:
    context.log.info(f"Product URL: {context.request.loaded_url}")


@router.handler(Labels.Download)
async def download_handler(context: CraftpixCrawlerContext) -> None:
    download_button = context.page.locator("a", has_text="Start Download")
    await download_button.wait_for(state="visible", timeout=16 * 1_000)

    async with context.page.expect_download() as download_info:
        await download_button.click()
    download = await download_info.value
    filepath = Path(context.storage.path, download.suggested_filename)
    await download.save_as(filepath)
