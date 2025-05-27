from importlib import import_module
from typing import List, cast
from pathlib import Path

from ._crawler import Crawler


root = Path(__file__).parent.parent
package = root.name

crawlers: List[Crawler] = []
for path in root.joinpath("crawlers").glob("*"):
    if path.name == "__pycache__" or not path.is_dir():
        continue
    module_name = f".{path.relative_to(root)}".replace("/", ".")
    module_args = dict(name=module_name, package=package)
    crawler: Crawler = cast(Crawler, import_module(**module_args).crawler)
    crawlers.append(crawler)
