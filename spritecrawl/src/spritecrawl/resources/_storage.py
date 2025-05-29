from dataclasses import dataclass
from pathlib import Path


@dataclass
class StorageResource:
    path: Path
