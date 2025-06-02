import pandas as pd

from pathlib import Path
from pandas import DataFrame
from typing import List, override, cast

from .._util import fetch_asset
from .._adapter import IterDataAdapter, Metadata


class PixelArtAdapter(IterDataAdapter):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.__data_file: Path = self._src_dir / "pixilart.parquet"
        self.__data: DataFrame

    @override
    def _init(self) -> None:
        self.__data = pd.read_parquet(self.__data_file, engine="pyarrow")

    def _write_item(self, index: int) -> None:
        row = self.__data.iloc[index]
        asset_url = row["full_image_url"]
        ext = asset_url.split(".")[-1]

        out_path = self._assets_dir.resolve().absolute() / f"asset_{index}.{ext}"
        status = fetch_asset(asset_url, out_path)
        if not status:
            raise Exception(f"Could not fetch asset {asset_url}. Stopping")

        self._metadata.append(
            Metadata(
                type="static" if ext == "png" else "animation",
                dataset=self._datasrc,
                path=str(out_path),
                url=asset_url,
            )
        )

    def _write_meta(self) -> None:
        pd.DataFrame(self._metadata).to_json(self._metadata_file, indent=2)

    def __len__(self) -> int:
        return len(self.__data)
