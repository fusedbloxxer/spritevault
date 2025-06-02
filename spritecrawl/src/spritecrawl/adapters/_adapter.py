import json

from tqdm import tqdm
from os import PathLike
from pathlib import Path
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Dict, List, Literal, Any, final


@dataclass
class DataSource:
    date: str
    source: str


@dataclass
class Metadata:
    url: str
    path: str
    dataset: DataSource
    type: Literal["static", "animation", "spritesheet"]


class DataAdapter(ABC):
    def __init__(self, *args, src_dir: PathLike, dst_dir: PathLike, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._src_dir: Path = Path(src_dir).resolve()
        self._dst_dir: Path = Path(dst_dir).resolve()

        self._metadata_file: Path = self._dst_dir / "metadata.json"
        self._assets_dir: Path = self._dst_dir / "assets"
        self._metadata: List[Metadata] = []

        with open(self._src_dir / ".." / "data.json", "r") as data_file:
            dataset_metadata: Dict[str, Any] = json.load(data_file)
            self._datasrc = DataSource(**dataset_metadata)

    def process(self) -> None:
        if self._skip:
            print(f"Adapter for {self._src_dir} was already ran. Skipping")
            return
        self._assets_dir.mkdir(parents=True, exist_ok=True)
        self._process()
        self._cleanup()

    @abstractmethod
    def _process(self) -> None:
        """Process the data source into target location."""
        pass

    def _cleanup(self) -> None:
        """Clean intermediary files during process."""
        pass

    @property
    def _skip(self) -> bool:
        return self._metadata_file.exists()


class IterDataAdapter(DataAdapter):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @final
    def _process(self) -> None:
        self._init()
        with tqdm(total=len(self), desc="Processing") as pbar:
            for index in range(len(self)):
                self._write_item(index)
                pbar.update(1)
        self._write_meta()

    def _init(self) -> None:
        pass

    @abstractmethod
    def _write_item(self, index: int) -> None:
        """Write a single item to disk."""
        pass

    @abstractmethod
    def _write_meta(self) -> None:
        """Write the metadata file for the dataset to disk."""
        pass

    @abstractmethod
    def __len__(self) -> int:
        """Number of elements to process from the given data."""
        pass
