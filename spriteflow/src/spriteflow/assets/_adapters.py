from dagster import asset

from spritecrawl.adapters import (
    PixelArtAdapter0,
    PixelArtAdapter1,
    PixelArtAdapter2,
    PixelArtAdapter3,
    PixelArtAdapter4,
    PixelArtAdapter5,
    PixelArtAdapter6,
)

@asset
async def pixelart_adapter_0() -> None:
    adapter = PixelArtAdapter0(src_dir="data/source/source-0/raw", dst_dir="data/source/source-0/out")
    adapter.process()


@asset
async def pixelart_adapter_1() -> None:
    adapter = PixelArtAdapter1(src_dir="data/source/source-1/raw", dst_dir="data/source/source-1/out")
    adapter.process()


@asset
async def pixelart_adapter_2() -> None:
    adapter = PixelArtAdapter2(src_dir="data/source/source-2/raw", dst_dir="data/source/source-2/out")
    adapter.process()


@asset
async def pixelart_adapter_3() -> None:
    adapter = PixelArtAdapter3(src_dir="data/source/source-3/raw", dst_dir="data/source/source-3/out")
    adapter.process()


@asset
async def pixelart_adapter_4() -> None:
    adapter = PixelArtAdapter4(src_dir="data/source/source-4/raw", dst_dir="data/source/source-4/out")
    adapter.process()


@asset
async def pixelart_adapter_5() -> None:
    adapter = PixelArtAdapter5(src_dir="data/source/source-5/raw", dst_dir="data/source/source-5/out")
    adapter.process()


@asset
async def pixelart_adapter_6() -> None:
    adapter = PixelArtAdapter6(src_dir="data/source/source-6/raw", dst_dir="data/source/source-6/out")
    adapter.process()
