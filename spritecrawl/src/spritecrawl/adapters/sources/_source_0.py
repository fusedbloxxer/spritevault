import os
import re
import shutil
import pandas as pd
import imageio.v3 as iio

from PIL import Image
from pathlib import Path
from zipfile import ZipFile
from typing import List, override

from .._adapter import IterDataAdapter, Metadata


class PixelArtAdapter(IterDataAdapter):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.__data_zip: Path = self._src_dir / "archive.zip"
        self.__data_files: List[Path] = []

    @override
    def _init(self) -> None:
        with ZipFile(self.__data_zip) as data_zip:
            data_zip.extractall(self._dst_dir)

        def image_index(path: Path) -> int:
            match = re.search(r"_(\d+)\.", str(path))
            return int(match.group(1)) if match else 0

        base_path = self._dst_dir / "images" / "images"
        self.__data_files = sorted(base_path.rglob("*.JPEG"), key=image_index)

    def _write_item(self, index: int) -> None:
        out_path = str(self._assets_dir.resolve().absolute() / f"image_{index}.png")
        img_path = str(self.__data_files[index].resolve().absolute())
        img_np = iio.imread(img_path)
        img = Image.fromarray(img_np)
        img.save(out_path)
        self._metadata.append(
            Metadata(
                url=self._datasrc.source,
                dataset=self._datasrc,
                type="static",
                path=out_path,
            )
        )

    def _write_meta(self) -> None:
        pd.DataFrame(self._metadata).to_json(self._metadata_file, indent=2)

    def __len__(self) -> int:
        return len(self.__data_files)

    @override
    def _cleanup(self) -> None:
        shutil.rmtree(self._dst_dir / "images")
        os.remove(self._dst_dir / "labels.csv")
        os.remove(self._dst_dir / "sprites.npy")
        os.remove(self._dst_dir / "sprites_labels.npy")
