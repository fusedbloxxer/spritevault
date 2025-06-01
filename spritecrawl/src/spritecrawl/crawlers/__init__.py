from dotenv import load_dotenv
import os

load_dotenv("/mnt/storage/git/spritevault/.env")
print(os.getenv("CRAWLEE_STORAGE_DIR"))

from ._router import RequiresContext
from ._crawler import Crawler
from .craftpix import *

__all__ = [
    "CraftpixResources",
    "CraftpixCrawler",
    "RequiresContext",
    "Crawler",
]
