import requests

from os import PathLike


def fetch_asset(url: str, path: PathLike) -> bool:
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading asset from {url}: {e}")
        return False
    except IOError as e:
        print(f"Error writing to file {path}: {e}")
        return False
