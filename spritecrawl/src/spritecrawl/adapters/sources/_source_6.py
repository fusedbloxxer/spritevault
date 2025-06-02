import io
import pandas as pd

from PIL import Image
from pathlib import Path
from typing import override
from pandas import DataFrame

from .._adapter import IterDataAdapter, Metadata


class PixelArtAdapter(IterDataAdapter):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.__data_file: Path = self._src_dir / "pixel-images.parquet"
        self.__data: DataFrame

    @override
    def _init(self) -> None:
        self.__data = pd.read_parquet(self.__data_file, engine="pyarrow")

    def _write_item(self, index: int) -> None:
        row = self.__data.iloc[index]
        img = Image.open(io.BytesIO(row["image"]["bytes"]))
        out_path = self._assets_dir / f"image_{index}.png"
        img.save(out_path)
        self._metadata.append(
            Metadata(
                url=self._datasrc.source,
                dataset=self._datasrc,
                path=str(out_path),
                type="static",
            )
        )

    def _write_meta(self) -> None:
        pd.DataFrame(self._metadata).to_json(self._metadata_file, indent=2)

    def __len__(self) -> int:
        return len(self.__data)
