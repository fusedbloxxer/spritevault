from typing import Callable, Generic, TypeVar, Any, Self, override
from collections.abc import Awaitable
from dataclasses import fields

from crawlee._types import BasicCrawlingContext
from crawlee.router import Router

from ._context import WebsiteContext


TCC = TypeVar("TCC", bound=BasicCrawlingContext)
TWC = TypeVar("TWC", bound=WebsiteContext)


class RouterWithContext(Generic[TCC, TWC], Router[TCC]):
    def __init__(self) -> None:
        super().__init__()
        self._context: TWC | None = None

    @override
    async def __call__(self, ctx: Any) -> None:
        """Invoke a request handler that matches the request label (or the default)."""
        if ctx.request.label is None or ctx.request.label not in self._handlers_by_label:
            if self._default_handler is None:
                raise RuntimeError(f"No handler matches label `{ctx.request.label}` and no default handler is configured")
            handler = self._default_handler
        else:
            handler = self._handlers_by_label[ctx.request.label]

        if self._context is not None:
            for field in fields(self._context):
                object.__setattr__(ctx, field.name, getattr(self._context, field.name))

        return await handler(ctx)

    def with_context(self, context: TWC) -> Self:
        self._context = context
        return self
