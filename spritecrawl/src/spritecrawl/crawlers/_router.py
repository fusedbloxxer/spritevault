from dataclasses import fields
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Self, List, override

from crawlee.router import Router
from crawlee._types import BasicCrawlingContext

from ._context import WebsiteContext


TCC = TypeVar("TCC", bound=BasicCrawlingContext)
TWC = TypeVar("TWC", bound=WebsiteContext)


class RequiresContext(Generic[TCC], ABC):
    @abstractmethod
    def accept(self, context: TCC) -> None:
        ...


class RouterWithContext(Generic[TCC, TWC], Router[TCC]):
    def __init__(self) -> None:
        super().__init__()
        self.__observers: List[RequiresContext[TCC]] = list()
        self.__context_overrides: TWC | None = None

    @override
    async def __call__(self, ctx: TCC) -> None:
        # Determine what handler to apply for the given context
        if ctx.request.label is None or ctx.request.label not in self._handlers_by_label:
            if self._default_handler is None:
                raise RuntimeError(f"No handler matches label `{ctx.request.label}` and no default handler is configured")
            handler = self._default_handler
        else:
            handler = self._handlers_by_label[ctx.request.label]

        # Apply context overrides to inject dependencies
        if self.__context_overrides is not None:
            for field in fields(self.__context_overrides):
                object.__setattr__(ctx, field.name, getattr(self.__context_overrides, field.name))

        # Give full context to observers
        self.__notify_observers(ctx)

        # Run handler
        return await handler(ctx)

    def with_context(self, context: TWC) -> Self:
        self.__context_overrides = context
        return self

    def with_observer(self, observer: RequiresContext[TCC]) -> Self:
        self.__observers.append(observer)
        return self

    def __notify_observers(self, context: TCC) ->None:
        for observer in self.__observers:
            observer.accept(context)

