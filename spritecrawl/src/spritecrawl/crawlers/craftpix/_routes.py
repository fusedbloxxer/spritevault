import os
import typing as t

from pathlib import Path
from crawlee import Request
from typing import Any, cast
from dataclasses import asdict

from ...resources import PixelArtAsset
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
    login_element = ctx.page.locator("a.lr-singin")
    await login_element.click()

    auth_form = ctx.page.locator("#auth-form")
    await auth_form.wait_for(state="visible")

    await auth_form.locator("#user_login").type(ctx.account.username, delay=25)
    await auth_form.locator("#user_pass").type(ctx.account.password, delay=25)
    await auth_form.locator("#submit-btn").click()

    account_element = ctx.page.locator('a > i[class="icon-account"]')
    await account_element.wait_for(state="visible")
    await ctx.page.wait_for_timeout(2000)

    seed_request = Request.from_url(ctx.seed_url, label=Labels.Category)
    await ctx.add_requests([seed_request])


@router.handler(Labels.Category)
async def category_handler(ctx: CraftpixCrawlerContext) -> None:
    ctx.log.info(f"Category: {ctx.request.loaded_url}")

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
    await ctx.database.mark_url(ctx.store.website_id, ctx.request.url)
    ctx.log.info(f"Freebie URL: {ctx.request.loaded_url}")

    download_button = ctx.page.locator("a.gtm-download-free").first
    link = await download_button.get_attribute("href")
    assert link, "Could not find download button for free asset!"

    asset = ctx.storage.create_asset()
    asset.text = ctx.request.url

    request = Request.from_url(link, label=Labels.Download)
    request.user_data["asset"] = asdict(asset)
    await ctx.add_requests([request])


@router.handler(Labels.Product)
async def product_handler(ctx: CraftpixCrawlerContext) -> None:
    await ctx.database.mark_url(ctx.store.website_id, ctx.request.url)
    ctx.log.info(f"Product URL: {ctx.request.loaded_url}")


@router.handler(Labels.Download)
async def download_handler(ctx: CraftpixCrawlerContext) -> None:
    download_button = ctx.page.locator("a", has_text="Start Download")
    await download_button.wait_for(state="visible", timeout=16 * 1_000)

    asset_url = await download_button.get_attribute("href")
    assert asset_url, "Could not extract asset url from the DOM!!"
    await ctx.database.mark_asset(ctx.store.website_id, asset_url)

    async with ctx.page.expect_download() as download_info:
        await download_button.click()
    download = await download_info.value

    async def download_asset(filepath: str):
        await download.save_as(filepath)

    asset = PixelArtAsset(**cast(Any, ctx.request.user_data["asset"]))
    asset.asset_ext = os.path.splitext(download.suggested_filename)[1]
    await ctx.storage.save_asset(asset, download_asset)
