from scrapy.http import response
from ..utils.parse_url import get_url_info
from ..database.create_db import create_page


def get_vocadb_query(original_url) -> str | None:
    """
    Vocadb API 쿼리를 생성하는 함수
    """
    url_info = get_url_info(original_url)

    if url_info is None:
        return None

    vocadb_api_url = "https://vocadb.net/api/songs"
    vocadb_query = f"{vocadb_api_url}/byPV?pvService={url_info['host']}&pvId={url_info['id']}&fields=PVs"
    return vocadb_query


def parse_vocadb(response: response):
    self = response.meta.get("self")
    page_info = response.meta.get("page_info")
    idx = response.meta.get("idx")
    song_info = page_info["songInfo"]
    vocadb_info = response.json()

    if vocadb_info is not None:
        song_info[idx]["vocadbId"] = vocadb_info["id"]
    else:
        song_info[idx]["vocadbId"] = None

    vocadb_filled = False
    for song in song_info:
        if "vocadbId" not in song:
            return
        vocadb_filled = True

    if vocadb_filled:
        self.info_list.append(page_info)
        create_page(page_info)
