import scrapy
from scrapy.http import response
from urllib.parse import urlparse
from ..spiders.wiki_class import LinkSpider
from ..utils.types import PageInfo
from .info_table import parse_table
from .lyrics import parse_lyrics
from .vocadb import get_vocadb_query, parse_vocadb
from ..database.create_db import create_page


def parse_song_page(self: LinkSpider, response: response):
    """
    곡 페이지의 정보를 파싱하는 함수
    """

    info_table_list = response.css(".info-table")
    page_info = PageInfo()

    page_url = urlparse(response.url).path
    page_info["pageUrl"] = page_url

    # 페이지 제목 파싱
    page_title = response.css("#page-title::text").get().strip()
    page_info["pageTitle"] = page_title

    # 원 제목 파싱
    original_title_text = (
        info_table_list[0].css(".info-table > tr:first-child *::text").getall()
    )
    original_title = "".join(original_title_text).strip()
    page_info["originalTitle"] = original_title

    if len(info_table_list) > 1:
        # table의 개수가 1개 이상인 경우 각 테이블에 대해서 정보를 파싱
        temp_info_list = []
        for table in info_table_list:
            song_info = parse_table(table)
            temp_info_list.append(song_info)

        # 표가 2개 이상인 경우는 없기에 2개에 대한 단순비교를 진행함
        # 그리고 두 표의 정보가 동일할 경우에는 니코동 링크가 있는 정보 1개만을 넣음
        info_list = []
        for temp_info in temp_info_list:
            # 표가 2개 이상인 경우에는 표를 나누지 않았기 때문에 각 리스트에 1개씩만의 song info만 존재함
            # 따라서 0번째 info를 가져와서 니코동 링크가 있는지 확인함
            if "nicovideo" in temp_info[0]["originalUrl"]:
                info_list.append(temp_info[0])
                break
    else:
        # table의 개수가 1개인 경우 해당 table에 대해서만 정보를 파싱
        info_list = parse_table(info_table_list[0])

    page_info["songInfo"] = info_list

    # 가사 파싱
    page_info["lyricsInfo"] = parse_lyrics(response)

    # Vocadb API 쿼리를 생성하고 Vocadb API에 요청을 보냄
    for song_info in page_info["songInfo"]:
        vocadb_query = get_vocadb_query(song_info["originalUrl"])
        if vocadb_query is None:
            song_info["vocadbId"] = None

    is_vocadb_full = True
    for song_info in page_info["songInfo"]:
        if "vocadbId" not in song_info:
            is_vocadb_full = False
            break

    if is_vocadb_full:
        self.info_list.append(page_info)
        create_page(page_info)
    else:
        for idx, song_info in enumerate(page_info["songInfo"]):
            vocadb_query = get_vocadb_query(song_info["originalUrl"])
            if vocadb_query is not None:
                yield scrapy.Request(
                    vocadb_query,
                    parse_vocadb,
                    meta={"page_info": page_info, "idx": idx, "self": self},
                )


def parse_song_redirects(self: LinkSpider, response: response):
    """
    곡 페이지의 리다이렉트 여부를 파싱하는 함수\\
    파싱한 결과를 LinkSpider.links에 추가함
    """
    try:
        # TODO: 기존의 links에 이미 링크가 존재하면 포함하지 않는 코드 추가

        # 곡 정보를 담은 table이 있는지 확인
        info_table_list = response.css(".info-table")
        if not info_table_list:
            redirect_links = response.css(
                "#page-content ul li a:not(.newpage)::attr(href)"
            ).getall()

            for redirect_link in redirect_links:
                # 리다이렉트 링크가 곡 뿐만 아니라 앨범 등을 가리키는 경우도 있음
                # 해당 경우에는 링크에 :이 들어감을 이용해서 제외함
                if ":" not in redirect_link and redirect_link not in self.links:
                    self.links.append(redirect_link)
                    self.debug_links.append(redirect_link)
                    response.follow(
                        redirect_link, lambda response: parse_song_page(self, response)
                    )
        else:
            # 만약 정보 테이블이 있으면 곡의 상대 url을 links에 추가함
            relative_path = urlparse(response.url).path
            if relative_path not in self.links:
                self.links.append(relative_path)
                self.debug_links.append(relative_path)
                parse_song_page(self, response)
    except Exception as e:
        self.error_links.append(response.url)
        self.logger.error(f"{e} at {response.url}")
