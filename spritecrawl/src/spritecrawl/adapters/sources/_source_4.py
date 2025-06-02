import pandas as pd

from pathlib import Path
from typing import List, override

from .._util import fetch_asset
from .._adapter import IterDataAdapter, Metadata


class PixelArtAdapter(IterDataAdapter):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.__asset_base_url = f"{self._datasrc.source}/resolve/main/train"
        self.__input_metadata_path: Path = self._src_dir / "metadata.jsonl"

    @override
    def _init(self) -> None:
        self.__metadata_input = pd.read_json(self.__input_metadata_path, lines=True)

    def _write_item(self, index: int) -> None:
        row = self.__metadata_input.iloc[index]
        asset_url = f"{self.__asset_base_url}/{row['file_name']}?download=true"
        ext = row["extension"]

        out_path = self._assets_dir.resolve().absolute() / f"asset_{index}.{ext}"
        # status = fetch_asset(asset_url, out_path)
        # if not status:
        #     raise Exception(f"Could not fetch asset {asset_url}. Stopping")

        self._metadata.append(
            Metadata(
                dataset=self._datasrc,
                path=str(out_path),
                type="animation",
                url=asset_url,
            )
        )

    def _write_meta(self) -> None:
        pd.DataFrame(self._metadata).to_json(self._metadata_file, indent=2)

    def __len__(self) -> int:
        return len(self.__metadata_input)
