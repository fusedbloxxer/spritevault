from dagster import Definitions

from .assets import all_assets
from .resources import all_resources


defs = Definitions(
    assets=all_assets,
    resources=all_resources,
)
