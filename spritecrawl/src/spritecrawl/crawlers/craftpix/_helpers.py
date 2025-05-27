from .._router import RouterWithContext

from ._context import CraftpixContext, CraftpixWebsiteContext

router = RouterWithContext[CraftpixContext, CraftpixWebsiteContext]()
