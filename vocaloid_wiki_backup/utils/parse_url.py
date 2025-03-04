from urllib.parse import urlparse
from typing import TypedDict


class UrlInfo(TypedDict):
    host: str | None
    id: str | None


def get_url_info(url: str | None) -> UrlInfo | None:
    if url is None:
        return None

    info = UrlInfo()

    url_obj = urlparse(url)
    host = url_obj.hostname

    if "nicovideo" in host:
        info["host"] = "NicoNicoDouga"
        info["id"] = url_obj.path.split("/")[-1]
    elif "youtube" in host:
        info["host"] = "YouTube"
        info["id"] = url_obj.query.split("=")[-1]

    return info
