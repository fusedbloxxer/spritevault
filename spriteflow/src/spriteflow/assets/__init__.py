from dagster import load_assets_from_modules

from . import _adapters, _crawlers


data_adapters_assets = load_assets_from_modules([_adapters], group_name="data_adapters")
data_crawlers_assets = load_assets_from_modules([_crawlers], group_name="data_crawlers")
all_assets = [*data_adapters_assets, *data_crawlers_assets]

__all__ = ["all_assets"]
