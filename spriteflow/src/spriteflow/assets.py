from dagster import asset
from dagster import AssetExecutionContext


@asset
def test(context: AssetExecutionContext) -> None:
    context.log.info("Sample test log")
