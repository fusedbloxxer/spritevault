import uuid
import json
import time
import aiofiles

from pathlib import Path
from datetime import datetime
from typing import Callable, Awaitable
from dataclasses import dataclass, asdict

from ..datatype import Asset
from ..extensions import DownloadOptions


@dataclass
class AssetManagerResource:
    save_dir: Path

    def __post_init__(self) -> None:
        self.save_dir.mkdir(exist_ok=True, parents=True)

    def create_asset(self, **kwargs) -> Asset:
        return Asset(
            timestamp=int(time.mktime(datetime.now().timetuple())),
            asset_id=str(uuid.uuid4()),
            **kwargs,
        )

    async def save_asset(
        self,
        asset: Asset,
        download_function: Callable[[DownloadOptions], Awaitable],
    ) -> None:
        assert len(asset.asset_url) != 0, "Found empty asset URL! Cannot download!"
        assert len(asset.asset_id) != 0, "Found no id on the given asset!"
        assert self.save_dir.exists(), "Save directory does not exist!"

        try:

            await download_function(
                DownloadOptions(
                    url=asset.asset_url,
                    dirpath=self.save_dir,
                    filename=asset.asset_id,
                )
            )
        except Exception as e:
            print(f"Error downloading asset from {asset.asset_url}: {e}")
            raise

        metadata_filename = f"{asset.asset_id}.json"
        metadata_filepath = self.save_dir / metadata_filename

        async with aiofiles.open(metadata_filepath, "w") as metadata_file:
            content = json.dumps(asdict(asset), indent=4)
            await metadata_file.write(content)
