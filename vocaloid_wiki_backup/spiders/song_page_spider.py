import scrapy
import json
import os
import re
from typing import TypedDict


table_info_essential = [
    {
        "name": "composer",
        "phrase": ["작곡", "작사작곡", "곡과 시"],
    },
    {
        "name": "lyricist",
        "phrase": ["작사", "작사 협력", "작사작곡", "곡과 시"],
    },
]

table_info_optional = [
    {
        "name": "arranger",
        "phrase": ["편곡", "재편곡", "브라스 편곡", "피아노 편곡"],
    },
    {
        "name": "singer",
        "phrase": ["노래", "나레이션", "대사", "피처링", "삐뽀삐뽀"],
    },
    {
        "name": "chorus",
        "phrase": ["코러스", "보컬 서포트"],
    },
    {
        "name": "vocaloid-editor",
        "phrase": ["조교", "음과 조교"],
    },
    {
        "name": "illustrator",
        "phrase": ["일러스트", "그림", "그림과 영상"],
    },
    {
        "name": "video",
        "phrase": ["영상", "그림과 영상"],
    },
    {
        "name": "engineering",
        "phrase": ["엔지니어링", "브라스 녹음 엔지니어", "레코딩"],
    },
    {
        "name": "mixing",
        "phrase": ["믹싱", "믹스", "보카로 믹싱 엔지니어"],
    },
    {
        "name": "mastering",
        "phrase": ["마스터링"],
    },
    {
        "name": "pianist",
        "phrase": ["피아노", "키보드", "신디사이저", "신스", "재즈피아노"],
    },
    {
        "name": "guitarist",
        "phrase": ["기타", "기타 솔로"],
    },
    {
        "name": "bassist",
        "phrase": ["베이스"],
    },
    {
        "name": "drummer",
        "phrase": ["드럼"],
    },
    {
        "name": "trumpeter",
        "phrase": ["트럼펫"],
    },
    {
        "name": "trombonist",
        "phrase": ["트럼본"],
    },
    {
        "name": "alto-saxophonist",
        "phrase": ["알토 색소폰"],
    },
    {
        "name": "player-etc",
        "phrase": ["연주", "원곡", "하이라이트", "밴드", "스크래치", "코러스 제작"],
    },
]


class Info(TypedDict):
    originalUrl: str
    pageTitle: str


class Song(TypedDict):
    pageUrl: str
    relativeUrl: str
    info: list[Info]


class SongSpider(scrapy.Spider):
    name = "vocaloid-wiki-table"
    urls = []
    info_dicts = []

    def start_requests(self):
        # url = "http://vocaro.wikidot.com/allsongs"
        # url = "http://vocaro.wikidot.com/mosaic-roll"  # 2개의 곡과 1개의 표가 있는 경우
        # url = "http://vocaro.wikidot.com/dance-robot-dance"  # 2개의 곡과 1개의 표가 있는 경우
        # url = "http://vocaro.wikidot.com/alive"  # 제목이 중복이라서 링크가 있는 경우
        # url = "http://vocaro.wikidot.com/brand-new-day"  # 2개의 정보 표가 존재하는 경우
        # url = "http://vocaro.wikidot.com/coaddiction"  # 일반적인 경우
        # url = "http://vocaro.wikidot.com/telecaster-b-boy"  # 가사 표가 2개 이상인 경우
        # url = "http://vocaro.wikidot.com/immature-discipline"  # 가사 표 2개 중 1개가 잘못된 경우
        url = "http://vocaro.wikidot.com/sing-a-song"  #  노래와 조교를 한 곳에 적어둔 경우

        # yield scrapy.Request(url, self.parse)
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

    def parse_song(self, response):
        info_dict = {
            "url": response.url,
            "relativeUrl": response.url.split("/")[-1],
            "info": [],
        }

        # 페이지 제목 크롤링
        # TODO: 나중에 중복되는 제목의 페이지를 크롤링할 경우 원래 제목을 추가하는 코드 작성
        page_title = response.css("#page-title::text").get().strip()
        info_dict["pageTitle"] = page_title

        # 정보표 크롤링링
        # 표가 2개인 경우 존재
        # 이 경우에는 표를 분리해서 적용해야 됨
        table_list = response.css(".info-table")
        if not table_list:
            # 표가 없고 중복되는 곡에 대해서 리다이렉트 링크가 걸려있는 경우
            links = response.css("#main-content ul li")
            for link in links:
                yield response.follow(
                    link.css("a::attr(href)").get(),
                    self.parse_song,
                )
        else:
            for table in table_list:
                # 정보를 담은 요소들은 전부 table의 tr내부에 존재함
                table_tr = table.css("tr")

                # 정보를 담은 테이블에서 첫번째 tr내부의 텍스트가 일본어 제목임
                # 아직은 해당 tr내부에는 th밖에 없음
                # 예외가 발생하면 추가적인 수정 필요
                original_title = table_tr[0].css("th::text").get()
                # 표가 두개인 경우 제목의 중복 저장 방지
                info_dict.setdefault("original_title", original_title)

                # 두번째 tr은 동영상 플레이어여서 세번째 tr부터 정보를 확인함
                # 세번째 tr은 일관되게 전부 출처를 담고 있음
                # getall로 요소를 가지고 와야 출처가 2개 이상인 경우를 다룰 수 있음
                original_url_list = table_tr[2].css("td a::attr(href)").getall()
                for original_url in original_url_list:
                    url = None if original_url == "" else original_url
                    info_dict["info"].append({"original_url": url})

                """
                출처는 2개 이상이 될 수 있지만 현재 찾은 경우는 2개가 최대임
                따라서 기본적으로 2개의 출처를 다루는 코드를 작성함
                출처가 2개인 경우에는 같은 요소가 있고 다른 요소가 있다
                같은 요소: 작곡, 작사
                다른 요소: 재편곡, 그 외
                다를 수도 있는 요소: 노래, 일러스트
                따라서 작곡과 작사는 동일하게 넣는다
                그러나 노래의 경우에는 같은 행에 2개의 노래 정보가 존재할 경우 따로 분리하고
                그 외의 편곡, 재편곡, 일러스트 같은 경우에는
                한 행에 2개 이상의 열이 존재할 때만 해당 행이 있는 열로 분리한다
                그리고 작곡&작사로 &, /, *을 통해서 여러 분야가 1개로 묶여있는 경우에는 이를 분리한다.
                단, 예외 케이스로 노래/조교, 코러스/조교의 형태로 노래와 조교를 같은 행에 넣는 경우가 있는데
                이는 따로 코드를 작성해서 분리한다
                """

                # 미리 분리한 출처가 2개 이상인지 확인
                has_multiple_original_urls = len(original_url_list) > 1

                # 네번째 tr부터 작사, 작곡 등 노래에 참여한 사람들의 정보를 담고 있음
                # 1개의 표에 2개의 영상이 담긴 경우도 존재하기에 이를 분리 해야함
                for tr_selector in table_tr[3:]:
                    tr_th = tr_selector.css("th::text").getall()
                    # td내부에 link가 없거나, link와 일반 텍스트가 혼재되어 있을 경우에 대한 처리
                    tr_td_text = "".join(tr_selector.css("td *::text").getall())
                    tr_td_text = tr_td_text.split("\n")
                    tr_td = []
                    for td_text in tr_td_text:
                        # <br>로 여러 명의 사람이 있는 경우에 대한 분리
                        td_split = [
                            t.strip()
                            for t in re.split(r"<br\s*/?>", td_text)
                            if t.strip()
                        ]
                        tr_td.append(td_split)

                    # 한 행에 있는 th와 td는 서로 짝지어지기 때문에 총 개수가 똑같음
                    # 따라서 zip을 통해서 묶어서 사용함
                    # th와 td의 열의 위치에 따라 어떤 동영상의 정보냐가 갈리기 때문에
                    # enumerate와 zip을 동시에 사용함
                    for idx, (th, td) in enumerate(zip(tr_th, tr_td)):
                        # 현재 행에 있는 열이 2개 이상인지 확인
                        has_multiple_columns_in_row = len(tr_th) > 1

                        # 작사&작곡, 작사*작곡, 작사/작곡 같은 경우에 대한 분리
                        # 노래/조교, 코러스/조교 같은 경우에 대한 분리도 포함
                        th_split = [text.strip() for text in re.split(r"[\/&\*]", th)]

                        # 노래/조교, 코러스/조교의 경우를 분리하기 위한 조건
                        # th_split에 2개 이상의 요소가 존재하고 거기에 조교가 포함되어 있는 경우
                        has_multiple_info_in_cell = len(th_split) > 1
                        is_vocaloid_edit = "조교" in th_split
                        td_contains_multiple_values = (
                            has_multiple_info_in_cell and is_vocaloid_edit
                        )

                        # 분리한 th를 루프를 돌면서 info에 해당 요소에 대한 td를 추가함
                        for th_s_idx, th_s in enumerate(th_split):
                            # 해당 구절이 작사, 작곡에 해당하는지 확인
                            is_in_essential = False
                            for table_info in table_info_essential:
                                if th_s in table_info["phrase"]:
                                    # 만약에 작사 작곡에 해당한다면 모든 url에 작사, 작곡 정보 추가
                                    for info in info_dict["info"]:
                                        info.setdefault(table_info["name"], td)
                                    is_in_essential = True
                                    break

                            # 작사, 작곡에 해당하는 경우에는 다음으로 넘어감
                            if is_in_essential:
                                continue

                            td_edited = (
                                [re.split(r"\s*\/\s*", td_text) for td_text in td]
                                if td_contains_multiple_values
                                else td
                            )

                            # 노래, 일러스트 같은 경우에 대한 분리
                            for table_info in table_info_optional:
                                if th_s in table_info["phrase"]:
                                    # 만약 노래/조교, 코러스/조교의 경우에 해당하는 경우
                                    # th의 요소를 분리해서 for문을 돌리는 중이기에
                                    # 해당 th의 요소가 몇번째인지 th_s_idx를 통해서 확인한 다음에
                                    # td의 요소를 분리한 td_edited에서 해당 인덱스에 있는 요소를 추가함
                                    if td_contains_multiple_values:
                                        info_dict["info"][idx].setdefault(
                                            table_info["name"], td_edited[th_s_idx]
                                        )
                                    # 만약 현재 출처가 2개 이상이고 현재 행에 있는 정보가 2개 이상인 경우
                                    # 현재 index에 해당하는 출처에 정보를 추가함
                                    elif (
                                        has_multiple_original_urls
                                        and has_multiple_columns_in_row
                                    ):
                                        info_dict["info"][idx].setdefault(
                                            table_info["name"], td
                                        )
                                    # 그 외의 경우에는 모든 url에 정보를 추가함
                                    else:
                                        for info in info_dict["info"]:
                                            info.setdefault(table_info["name"], td)
                                    break

            # 표가 2개(이상)인 경우 두 표가 링크 이외에 전부 동일한지 확인
            # 이때 동일하다면 2개의 표를 1개로 합침
            # 이 경우 original_url은 원래 보카로 가사 위키처럼 니코동을 우선시함
            # 현재는 표가 2개 이상인 경우는 존재하지 않으므로 2개를 비교하는 코드만 작성
            if len(table_list) > 1:
                info_a = info_dict["info"][0]
                info_b = info_dict["info"][1]

                # 두 표의 정보가 동일한지 확인
                is_same = True
                if set(info_a.keys()) != set(info_b.keys()):
                    is_same = False
                else:
                    for key in info_a.keys():
                        if key != "original_url" and info_a[key] != info_b[key]:
                            is_same = False
                            break

                if is_same:
                    if "nicovideo.jp" in info_a["original_url"]:
                        info_dict["info"] = [info_a]
                    else:
                        info_dict["info"] = [info_b]

        # 가사 정보 추가
        lyrics_table_list = response.css(".wiki-content-table")
        updated_lyrics_table_list = []
        # 가사 표가 2개 이상인 경우
        if len(lyrics_table_list) > 1:
            for lyrics_table in lyrics_table_list:
                # 가사 표가 2개가 동일한 가사 표인 경우가 있음
                # 이 경우 현재까지 발견된 오류는 처음 표시된 가사표가 끊겨있고 마지막 행이 비어있다는 공통점이 있음
                # 이를 통해서 잘못된 가사표를 걸러낼 수 있음
                # TODO: 추후 사이트가 수정된다면 잘못된 가사표를 걸러내는 다른 방법이 필요함
                last_lyrics = lyrics_table.css(
                    "tr:last-child td::text, tr:last-child th::text"
                ).get()
                if last_lyrics:
                    updated_lyrics_table_list.append(lyrics_table)

        # 업데이트 된 가사표로 새로 가사를 크롤링함
        for idx, lyrics_table in enumerate(updated_lyrics_table_list):
            lyrics = lyrics_table.css("tr th::text, tr td::text").getall()
            # 이때 가사표가 2개 이상일 경우 동영상의 배치 순서 (왼>오)에 따라 가사도 배치되어 있다고 가정해
            # 동영상의 순서대로 가사를 배치함
            info_dict["info"][idx].setdefault("lyrics", lyrics)

        with open(f"{info_dict['relativeUrl']}.json", "w", encoding="utf-8") as f:
            json.dump(info_dict, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    pass
