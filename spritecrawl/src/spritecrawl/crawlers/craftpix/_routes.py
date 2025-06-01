import os
import typing as t

from crawlee import Request
from typing import Any, cast
from dataclasses import asdict
from urllib.parse import urlparse

from ...extensions import DownloadOptions
from ...resources import Asset
from .._router import RouterWithContext
from ._context import CraftpixWebsiteContext
from ._context import CraftpixCrawlerContext
from ._common import Labels


router = RouterWithContext[CraftpixCrawlerContext, CraftpixWebsiteContext]()


@router.default_handler
async def default_handler(ctx: CraftpixCrawlerContext) -> None:
    raise RuntimeError(f"Unmatched request found: {ctx.request.loaded_url}")


@router.handler(Labels.Login)
async def login_handler(ctx: CraftpixCrawlerContext) -> None:
    ctx.log.info(f'Visiting login page at: {ctx.request.loaded_url}')

    login_element = ctx.page.locator("a.lr-singin")
    await login_element.click()

    auth_form = ctx.page.locator("#auth-form")
    await auth_form.wait_for(state="visible")

    ctx.log.info(f'Entering credentials for user: {ctx.account.username}')
    await auth_form.locator("#user_login").type(ctx.account.username, delay=25)
    await auth_form.locator("#user_pass").type(ctx.account.password, delay=25)
    await auth_form.locator("#submit-btn").click()

    account_element = ctx.page.locator('a > i[class="icon-account"]')
    await account_element.wait_for(state="visible")
    await ctx.page.wait_for_timeout(2000)

    ctx.log.info(f'Logged in successfully. Continue to scrape content at: {ctx.seed_url}')
    seed_request = Request.from_url(ctx.seed_url, label=Labels.Category)
    await ctx.add_requests([seed_request])


@router.handler(Labels.Category)
async def category_handler(ctx: CraftpixCrawlerContext) -> None:
    ctx.log.info(f"Category page: {ctx.request.loaded_url}")

    heading_element = ctx.page.locator("h1", has_text="Pixel Art Sprites")
    await heading_element.wait_for(state="visible")

    article_element = ctx.page.locator("article[data-item-id] .blog-grid-item > a")
    articles = await article_element.evaluate_all("(e) => e.map(x => x.href)")
    assets: t.List[Request] = []

    for article in articles:
        if "freebie" in article:
            assets.append(Request.from_url(article, label=Labels.Freebie))
            continue
        if "product" in article:
            assets.append(Request.from_url(article, label=Labels.Product))
            continue
        ctx.log.error(f"Unmatched article URL {article}. Will not crawl.")

    flags = await ctx.database.are_crawled([asset.url for asset in assets])
    assets = [asset for asset, asset_exists in zip(assets, flags) if not asset_exists]
    await ctx.add_requests(requests=assets)

    next_page_anchor = ctx.page.locator('a[class="nextpostslink"]').first
    has_next_page = await next_page_anchor.is_visible()
    if not has_next_page:
        return

    next_page = await next_page_anchor.get_attribute("href")
    assert next_page, "Next page button is visible but cannot retrieve its URL"
    await ctx.add_requests([Request.from_url(next_page, label=Labels.Category)])


@router.handler(Labels.Freebie)
async def freebie_handler(ctx: CraftpixCrawlerContext) -> None:
    ctx.log.info(f"Found freebie asset at: {ctx.request.loaded_url}")

    # Find relevant elements
    description_elem = ctx.page.locator('div[itemprop="description"]')
    title_elem = ctx.page.locator("h1.product_title")
    tag_elems = ctx.page.locator("ul.tags a")

    # Extract metadata from asset page
    asset = ctx.storage.create_asset()

    # Fill in shared data
    asset.asset_page = ctx.request.url
    asset.title = await title_elem.inner_text()
    asset.text = await description_elem.inner_text()
    asset.website = urlparse(ctx.seed_url).netloc
    tag_values = await tag_elems.all_text_contents()
    tag_values = [tag_content.replace("#", "") for tag_content in tag_values]
    asset.tags = tag_values

    # Proceed to download page
    download_button = ctx.page.locator("a.gtm-download-free").first
    link = await download_button.get_attribute("href")
    assert link, "Could not find download button for free asset!"

    request = Request.from_url(link, label=Labels.FreeDownload)
    request.user_data["asset"] = asdict(asset)
    await ctx.add_requests([request])


@router.handler(Labels.FreeDownload)
async def free_download_handler(ctx: CraftpixCrawlerContext) -> None:
    ctx.log.info(f"Downloading free asset at: {ctx.request.loaded_url}")

    download_button = ctx.page.locator("a", has_text="Start Download")
    await download_button.wait_for(state="visible", timeout=30 * 1_000)

    asset_url = await download_button.get_attribute("href")
    assert asset_url, "Could not extract asset url from the DOM!!"

    asset = Asset(**cast(Any, ctx.request.user_data["asset"]))
    asset.asset_url = asset_url

    async def download_asset(options: DownloadOptions):
        await ctx.helper.download_from_url(options)

    await ctx.storage.save_asset(asset, download_asset)
    await ctx.database.mark_url(ctx.store.website_id, asset.asset_page)
    await ctx.database.mark_asset(ctx.store.website_id, asset.asset_url)
    ctx.log.info(f"Successfully downloaded asset: {asset.asset_url}")


@router.handler(Labels.Product)
async def product_handler(ctx: CraftpixCrawlerContext) -> None:
    ctx.log.info(f"Found premium asset at: {ctx.request.loaded_url}")

    # Find relevant elements
    preview_elems = ctx.page.locator("figure.single-post-thumbnail > a")
    description_elem = ctx.page.locator('div[itemprop="description"]')
    demo_elems = description_elem.locator("img[src]")
    title_elem = ctx.page.locator("h1.product_title")
    tag_elems = ctx.page.locator("ul.tags a")

    # Load lazy content
    await ctx.helper.scroll_to_bottom()

    # Grab all assets
    preview_urls = await preview_elems.evaluate_all("(e) => e.map(x => x.href)")
    demo_urls = await demo_elems.evaluate_all("(e) => e.map(x => [x.src, x.classList.contains('lazy-hidden')])")
    demo_urls = [demo_url[0] for demo_url in demo_urls if not demo_url[1]]
    asset_urls = list(preview_urls) + list(demo_urls)

    requests: t.List[Request] = []
    for asset_url in asset_urls:
        asset = ctx.storage.create_asset()

        # Fill in shared data across similar assets
        asset.asset_url = asset_url
        asset.asset_page = ctx.request.url
        asset.title = await title_elem.inner_text()
        asset.text = await description_elem.inner_text()
        asset.website = urlparse(ctx.seed_url).netloc
        tag_values = await tag_elems.all_text_contents()
        tag_values = [tag_content.replace("#", "") for tag_content in tag_values]
        asset.tags = tag_values

        request = Request.from_url(asset_url, label=Labels.PreviewDownload)
        request.user_data["asset"] = asdict(asset)
        requests.append(request)
    await ctx.add_requests(requests)
    await ctx.database.mark_url(ctx.store.website_id, ctx.request.url)


@router.handler(Labels.PreviewDownload)
async def preview_download_handler(ctx: CraftpixCrawlerContext) -> None:
    ctx.log.info(f"Preview URL: {ctx.request.loaded_url}")

    async def download_asset(options: DownloadOptions):
        await ctx.helper.download_from_url(options)

    asset = Asset(**cast(Any, ctx.request.user_data["asset"]))
    await ctx.storage.save_asset(asset, download_asset)
    await ctx.database.mark_asset(ctx.store.website_id, asset.asset_url)
