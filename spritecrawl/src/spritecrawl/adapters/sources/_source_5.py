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
        self.__temp_dir: Path = self._dst_dir / "tmp"
        self.__in_dir: Path = self.__temp_dir / "Multi-cell pixel art"
        self.__data_files: List[Path] = []

    @override
    def _init(self) -> None:
        with ZipFile(self.__data_zip) as data_zip:
            data_zip.extractall(self.__temp_dir)

        def image_index(path: Path) -> str:
            return path.name

        self.__data_files = sorted(self.__in_dir.rglob("*.png"), key=image_index)

    def _write_item(self, index: int) -> None:
        img_path = self.__data_files[index].resolve().absolute()
        img_name = img_path.name
        out_path = self._assets_dir.resolve().absolute() / f"image_{img_name}"

        img_np = iio.imread(img_path)
        img = Image.fromarray(img_np)
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
        return len(self.__data_files)

    @override
    def _cleanup(self) -> None:
        shutil.rmtree(self.__temp_dir)
