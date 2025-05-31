import os
import uuid
import json
import time

from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Callable, Awaitable, Dict, Any


@dataclass(kw_only=True)
class PixelArtAsset:
    text: str = ""
    group: str = ""
    title: str = ""
    artist: str = ""
    website: str = ""
    asset_id: str = ""
    asset_url: str = ""
    asset_ext: str = ""
    timestamp: int = 0
    tags: List[str] = field(default_factory=list)


@dataclass
class AssetManagerResource:
    save_dir: Path

    def __post_init__(self) -> None:
        self.save_dir.mkdir(exist_ok=True, parents=True)

    def create_asset(self, **kwargs) -> PixelArtAsset:
        return PixelArtAsset(
            timestamp=int(time.mktime(datetime.now().timetuple())),
            asset_id=str(uuid.uuid4()),
            **kwargs,
        )

    async def save_asset(
        self,
        asset: PixelArtAsset,
        download_function: Callable[[str], Awaitable],
    ) -> None:
        asset_filename = f"{asset.asset_id}.{asset.asset_ext}"
        asset_filepath = self.save_dir / asset_filename

        try:
            await download_function(asset_filepath)
        except Exception as e:
            print(f"Error downloading asset from {asset.asset_url}: {e}")
            raise

        metadata_filename = f"{asset.asset_id}.json"
        metadata_filepath = self.save_dir / metadata_filename

        with open(metadata_filepath, "w") as metadata_file:
            json.dump(asdict(asset), metadata_file, indent=4)
        print(f"""Asset saved to {asset_filepath} and content to {metadata_filepath}""")
