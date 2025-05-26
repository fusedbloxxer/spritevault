from dotenv import load_dotenv
import os


load_dotenv()


def crawlers() -> None:
    print("hello!!")


def main() -> None:
    print(os.getenv("CRAWLEE_STORAGE_DIR"))
