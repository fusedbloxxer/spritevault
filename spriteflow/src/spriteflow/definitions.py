from dagster import Definitions
from dagster import load_assets_from_modules

from . import assets

all_assets = load_assets_from_modules([assets])

defs = Definitions(assets=all_assets)
