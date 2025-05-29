from dagster import Definitions
from dagster import load_assets_from_modules

from . import assets
from .resources import all_resources


all_assets = load_assets_from_modules([assets])


defs = Definitions(
    assets=all_assets,
    resources=all_resources,
)
