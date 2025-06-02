from typing import List
from dataclasses import dataclass, field


@dataclass(kw_only=True)
class Asset:
    text: str = ""
    group: str = ""
    title: str = ""
    artist: str = ""
    website: str = ""
    asset_id: str = ""
    asset_url: str = ""
    asset_page: str = ""
    timestamp: int = 0
    tags: List[str] = field(default_factory=list)


__all__ = ["Asset"]
