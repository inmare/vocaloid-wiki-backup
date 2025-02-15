import scrapy
import json
import os
import re
from typing import TypedDict
from urllib.parse import urlparse
import sys

# root폴더를 sys.path에 추가해서 절대 경로가 작동하도록 함
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.types import PageInfo, SongInfo, LyricsInfo, SONG_META_INFO


def find_meta_from_name(name):
    return list(filter(lambda meta: meta["name"] == name, SONG_META_INFO))[0]


def put_data_to_info(
    info_list, current_info, phrase_text, data, has_multiple_url, has_single_pair
):
    for meta in SONG_META_INFO:
        if phrase_text in meta["phrase"]:
            if meta["mustSame"] or (has_multiple_url and has_single_pair):
                for info in info_list:
                    info[meta["name"]] = data
            else:
                current_info[meta["name"]] = data
            break


class SongSpider(scrapy.Spider):
    name = "vocaloid-wiki-table"

    def start_requests(self):
        # allsongs_url = "http://vocaro.wikidot.com/allsongs"

        urls = [
            "http://vocaro.wikidot.com/coaddiction",  # 일반적인 경우
            "http://vocaro.wikidot.com/raise",  # 원본 링크가 없는 경우
            "http://vocaro.wikidot.com/mosaic-roll",  # 2개의 곡과 1개의 표가 있는 경우
            "http://vocaro.wikidot.com/dance-robot-dance",  # 2개의 곡과 1개의 표가 있는 경우
            "http://vocaro.wikidot.com/alive",  # 제목이 중복이라서 링크가 있는 경우
            "http://vocaro.wikidot.com/brand-new-day",  # 2개의 정보 표가 존재하는 경우
            "http://vocaro.wikidot.com/telecaster-b-boy",  # 가사 표가 2개 이상인 경우
            "http://vocaro.wikidot.com/immature-discipline",  # 가사 표 2개 중 1개가 잘못된 경우
            "http://vocaro.wikidot.com/sing-a-song",  #  노래와 조교를 한 곳에 적어둔 경우
        ]

        for url in urls:
            yield scrapy.Request(url, self.parse_song)

    def parse(self, response):
        card_css = "#page-content ul"

        for card in response.css(card_css):
            for link in card.css("li a"):
                page_url = link.css("::attr(href)").get()
                yield response.follow(page_url, self.parse_song)

    def parse_song_page(self, response):
        song_css = "#page-content > p"

        for song in response.css(song_css):
            yield response.follow(song.css("a::attr(href)").get(), self.parse_song)

    def parse_song(self, response, meta={}):
        table_list = response.css(".info-table")

        if not table_list:
            # table이 없을 경우 리다이렉트 링크를 가지고 있기 때문에 해당 링크들을 가져옴
            redirect_links = response.css("#page-content ul li a::attr(href)").getall()
            for link in redirect_links:
                # 그리고 그 링크들을 타고 들어가서 동일한 작업을 진행함
                yield response.follow(link, self.parse_song, meta={"redirect": True})
        else:
            page_url = urlparse(response.url).path
            page_info = PageInfo(
                pageUrl=page_url,
            )

            # 페이지 제목 파싱
            page_title = response.css("#page-title::text").get().strip()
            page_info["pageTitle"] = page_title

            # 중복된 제목으로 리다이렉트 되었을 때 제목/작곡가 형태의 제목을 파싱함
            # 그 후 진짜 제목을 따로 저장
            if response.meta.get("redirect"):
                original_page_title = page_title.split("/")[0]
                page_info["originalPageTitle"] = original_page_title

            # 원 제목 파싱
            original_title_text = table_list[0].css("tr:first-child *::text").getall()
            original_title = "".join(original_title_text).strip()
            page_info["originalTitle"] = original_title

            if len(table_list) > 1:
                # table의 개수가 1개 이상인 경우 각 테이블에 대해서 정보를 파싱
                temp_info_list = []
                for table in table_list:
                    info = self.parse_table(table)
                    temp_info_list.append(info)

                # 표가 2개 이상인 경우는 없기에 2개에 대한 단순비교를 진행함
                # 그리고 두 표의 정보가 동일할 경우에는 니코동 링크가 있는 정보 1개만을 넣음
                info_list = []
                for temp_info in temp_info_list:
                    # 표가 2개 이상인 경우에는 표를 나누지 않았기 때문에 각 리스트에 1개씩만의 song info만 존재함
                    # 따라서 0번째 info를 가져와서 니코동 링크가 있는지 확인함
                    if "nicovideo" in temp_info[0]["originalUrl"]:
                        info_list.append(temp_info[0])
                        break

                page_info["songInfo"] = info_list
            else:
                # table의 개수가 1개인 경우 해당 table에 대해서만 정보를 파싱
                info_list = self.parse_table(table_list[0])
                page_info["songInfo"] = info_list

            # 가사 파싱
            lyrics_selector = response.css(".wiki-content-table")
            page_info["lyricsInfo"] = self.parse_lyrics(response, lyrics_selector)

            with open(f"json/temp/{page_url}.json", "w", encoding="utf-8") as f:
                json.dump(page_info, f, indent=2, ensure_ascii=False)

    def parse_table(self, table_selector):
        info_list = []

        # table의 tr 태그들을 가져옴
        # 이때 1번째 tr은 원 제목, 2번째 tr은 동영상 플레이어기에 3번째 tr부터 가져옴
        tr_list = table_selector.css("tr")

        # 원본 URL 파싱
        original_url_list = tr_list[2].css("a::attr(href)").getall()
        for original_url in original_url_list:
            if original_url == "":
                info = SongInfo(originalUrl=None)
            else:
                info = SongInfo(originalUrl=original_url)
            info_list.append(info)

        # 원본 url이 2개 이상인지 확인
        has_multiple_url = len(original_url_list) > 1

        # 만약 원본 url이 2개 이상이라면 그 밑의 tr에서 정보가 나누어질 때 맞는 위치에 넣어야 함
        # 이때 위치는 원본 url 배치 순서를 따름
        for tr in tr_list[3:]:
            # 각 tr에서 th와 td를 모두 가져옴
            th_selector_list = tr.css("th")
            td_selector_list = tr.css("td")

            selector_pair = zip(th_selector_list, td_selector_list)
            # th와 td가 1개씩만 있는지 확인
            has_single_pair = len(th_selector_list) == 1

            for pair_idx, (th_selector, td_selector) in enumerate(selector_pair):
                current_info = info_list[pair_idx]

                # th와 td를 한 묶음으로 가져온 다음에 각각의 text를 가져옴
                th_text = th_selector.css("*::text").get()
                td_text_list = td_selector.css("*::text").getall()
                td_text_list = "".join(td_text_list).strip().split("\n")

                # th가 여러 개의 정보를 가지고 있는지 확인
                has_multiple_th = re.search(r"[&*\/]", th_text)
                if has_multiple_th:
                    # 만약 그렇다면 th를 분리해서 list로 만듦
                    th_text_list = re.split(r"[&*\/]", th_text)

                    # th가 노래/조교, 코러스/조교일 경우 td에도 음합엔/조교자의 형태로 여러가지 정보가 있음
                    # 이를 확인하기 위해 조교에 해당하는 phrase를 찾음
                    phrase_vocaloid_editor = find_meta_from_name("vocaloidEditor")[
                        "phrase"
                    ]
                    # 조교가 th에 있는지 확인
                    has_vocaloid_editor_phrase = any(
                        map(
                            lambda phrase: phrase in th_text_list,
                            phrase_vocaloid_editor,
                        )
                    )

                    # td를 분리해야 하는경우 분리해서 각각의 정보를 만듦
                    if has_vocaloid_editor_phrase:
                        # td가 여러 개인 경우는 (노래, 코러스)/조교 뿐이므로 정보를 2개의 list로 분리
                        singer_list = []
                        vocaloid_editor_list = []

                        for text in td_text_list:
                            td_split = re.split(r"\s*\/\s*", text)
                            singer_list.append(td_split[0])
                            vocaloid_editor_list.append(td_split[1])

                        name_singer = find_meta_from_name("singer")["name"]
                        name_vocaloid_editor = find_meta_from_name("vocaloidEditor")[
                            "name"
                        ]

                        # 겹치는 이름 제거
                        current_info[name_singer] = list(set(singer_list))
                        current_info[name_vocaloid_editor] = list(
                            set(vocaloid_editor_list)
                        )
                    else:
                        # td가 여러개가 아닌 경우 th 리스트의 th들에 기존 정보를 넣음
                        for th_text_item in th_text_list:
                            put_data_to_info(
                                info_list,
                                current_info,
                                th_text_item,
                                td_text_list,
                                has_multiple_url,
                                has_single_pair,
                            )
                else:
                    # th가 여러개가 아닌 경우 그냥 th와 td를 비교해서 정보를 넣음
                    put_data_to_info(
                        info_list,
                        current_info,
                        th_text,
                        td_text_list,
                        has_multiple_url,
                        has_single_pair,
                    )

        return info_list

    def parse_lyrics(self, response, lyrics_selector):
        fixed_lyrics_selector = lyrics_selector

        # 가사 표가 2개 이상인 경우
        if len(lyrics_selector) > 1:
            for lyrics_table in lyrics_selector:
                # 가사 표가 2개가 동일한 가사 표인 경우가 있음
                # 이 경우 현재까지 발견된 오류는 처음 표시된 가사표가 끊겨있고 마지막 행이 비어있다는 공통점이 있음
                # 이를 통해서 잘못된 가사표를 걸러낼 수 있음
                # TODO: 추후 사이트가 수정된다면 잘못된 가사표를 걸러내는 다른 방법이 필요함
                last_lyrics = (
                    lyrics_table.css("tr:last-child").css("td::text, th::text").get()
                )
                if not last_lyrics:
                    fixed_lyrics_selector = [lyrics_table]

        lyrics_info_list = []

        # 업데이트 된 가사표로 새로 가사를 크롤링함
        for lyrics_table in fixed_lyrics_selector:
            lyrics = lyrics_table.css("tr").css("th::text, td::text").getall()
            # 이때 가사표가 2개 이상일 경우 동영상의 배치 순서 (왼>오)에 따라 가사도 배치되어 있다고 가정함
            # 동영상의 순서대로 가사를 배치함
            lyrics_info = LyricsInfo(lyrics=lyrics)
            lyrics_info_list.append(lyrics_info)

        table_wrap = response.css(".table-wrap")
        if table_wrap:
            lyrics_versions = table_wrap.css("h2 span::text").getall()
            for idx, version in enumerate(lyrics_versions):
                lyrics_info_list[idx]["version"] = version

        return lyrics_info_list


if __name__ == "__main__":
    pass
