import scrapy
import json
import os
import re
from typing import TypedDict
from urllib.parse import urlparse

# json화를 용이하게 하기 위해서 python이지만 camelcase를 사용함

table_info_same = [
    {
        "name": "composer",
        "phrase": ["작곡", "작사작곡", "곡과 시"],
    },
    {
        "name": "lyricist",
        "phrase": ["작사", "작사 협력", "작사작곡", "곡과 시"],
    },
]

table_info_diff = [
    {
        "name": "singer",
        "phrase": ["노래", "나레이션", "대사", "피처링", "삐뽀삐뽀"],
    },
    {
        "name": "arranger",
        "phrase": ["편곡", "재편곡", "브라스 편곡", "피아노 편곡"],
    },
    {
        "name": "chorus",
        "phrase": ["코러스", "보컬 서포트"],
    },
    {
        "name": "vocaloidEditor",
        "phrase": ["조교", "음과 조교"],
    },
    {
        "name": "illustrator",
        "phrase": ["일러스트", "그림", "그림과 영상"],
    },
    {
        "name": "videoProducer",
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
        "name": "altoSaxophonist",
        "phrase": ["알토 색소폰"],
    },
    {
        "name": "playerEtc",
        "phrase": ["연주", "원곡", "하이라이트", "밴드", "스크래치", "코러스 제작"],
    },
]


class SongInfo(TypedDict):
    originalUrl: str
    lyrics: list[str]
    # 곡에 참여한 사람, 음합엔
    composer: list[str]
    lyricist: list[str]
    singer: list[str]
    arranger: list[str] | None = None
    chorus: list[str] | None = None
    vocaloidEditor: list[str] | None = None
    illustrator: list[str] | None = None
    videoProducer: list[str] | None = None
    engineering: list[str] | None = None
    mixing: list[str] | None = None
    mastering: list[str] | None = None
    pianist: list[str] | None = None
    guitarist: list[str] | None = None
    bassist: list[str] | None = None
    drummer: list[str] | None = None
    trumpeter: list[str] | None = None
    trombonist: list[str] | None = None
    altoSaxophonist: list[str] | None = None
    playerEtc: list[str] | None = None


class PageInfo(TypedDict):
    pageUrl: str  # 페이지 URL, 상대 경로
    pageTitle: str  # 번역된 제목, 중복된 제목의 경우 작곡가가 제목에 포함될 수 있음
    originalPageTitle: str | None = None  # 중복된 제목의 경우 작곡가를 제외한 원래 제목
    originalTitle: str  # 원 제목
    songInfo: list[SongInfo]
    lyrics: list[list[str]]


class SongSpider(scrapy.Spider):
    name = "vocaloid-wiki-table"

    def start_requests(self):
        # url = "http://vocaro.wikidot.com/allsongs"
        # url = "http://vocaro.wikidot.com/coaddiction"  # 일반적인 경우
        # url = "http://vocaro.wikidot.com/raise"  # 원본 링크가 없는 경우
        # url = "http://vocaro.wikidot.com/mosaic-roll"  # 2개의 곡과 1개의 표가 있는 경우
        # url = "http://vocaro.wikidot.com/dance-robot-dance"  # 2개의 곡과 1개의 표가 있는 경우
        # url = "http://vocaro.wikidot.com/alive"  # 제목이 중복이라서 링크가 있는 경우
        # url = "http://vocaro.wikidot.com/brand-new-day"  # 2개의 정보 표가 존재하는 경우
        # url = "http://vocaro.wikidot.com/telecaster-b-boy"  # 가사 표가 2개 이상인 경우
        # url = "http://vocaro.wikidot.com/immature-discipline"  # 가사 표 2개 중 1개가 잘못된 경우
        # url = "http://vocaro.wikidot.com/sing-a-song"  #  노래와 조교를 한 곳에 적어둔 경우
        urls = [
            # "http://vocaro.wikidot.com/coaddiction",
            # "http://vocaro.wikidot.com/raise",
            # "http://vocaro.wikidot.com/mosaic-roll",
            # "http://vocaro.wikidot.com/dance-robot-dance",
            # "http://vocaro.wikidot.com/alive",
            "http://vocaro.wikidot.com/brand-new-day",
            "http://vocaro.wikidot.com/telecaster-b-boy",
            # "http://vocaro.wikidot.com/immature-discipline",
            # "http://vocaro.wikidot.com/sing-a-song",
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

    def parse_song(self, response):
        parsed_url = urlparse(response.url)
        page_dict: PageInfo = {
            "pageUrl": parsed_url.path,
            "songInfo": [],
            "lyrics": [],
        }

        # 페이지 제목 크롤링
        # TODO: 나중에 중복되는 제목의 페이지를 크롤링할 경우 원래 제목을 추가하는 코드 작성
        page_title = response.css("#page-title::text").get().strip()
        page_dict["pageTitle"] = page_title

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
            return
        else:
            for table_idx, table in enumerate(table_list):
                # 정보를 담은 요소들은 전부 table의 tr내부에 존재함
                tr_selector = table.css("tr")

                # 정보를 담은 테이블에서 첫번째 tr내부의 텍스트가 일본어 제목임
                # 아직은 해당 tr내부에는 th밖에 없음
                # 예외가 발생하면 추가적인 수정 필요
                original_title = tr_selector[0].css("th::text").get()
                # 표가 두개인 경우 제목의 중복 저장 방지
                page_dict["originalTitle"] = page_dict.setdefault(
                    "originalTitle", original_title
                )

                # 두번째 tr은 동영상 플레이어여서 세번째 tr부터 정보를 확인함
                # 세번째 tr은 일관되게 전부 출처를 담고 있음
                # getall로 요소를 가지고 와야 출처가 2개 이상인 경우를 다룰 수 있음
                # 링크가 없는 경우에도 a태그는 여전히 존재하기에 실제로 가져오는 링크는 ""인 경우도 존재함
                original_url_list = tr_selector[2].css("td a::attr(href)").getall()
                # original url의 개수만큼 SongInfo TypedDict를 생성하고 songInfo에 추가함
                for original_url in original_url_list:
                    is_url_empty = original_url == ""
                    song_info: SongInfo = {
                        "originalUrl": original_url if not is_url_empty else None
                    }
                    page_dict["songInfo"].append(song_info)

                # 네번째 tr부터 작사, 작곡 등 노래에 참여한 사람들의 정보를 담고 있음
                # 1개의 표에 2개의 영상이 담긴 경우도 존재하기에 이를 분리 해야함
                for tr_selector in tr_selector[3:]:
                    # tr 내부에 있는 th와 td를 가져옴
                    # 이때 th는 제목이고 td는 정보를 담고 있기에 둘의 개수는 동일함
                    th_selector_list = tr_selector.css("th")
                    td_selector_list = tr_selector.css("td")

                    # 한 행에 있는 th와 td는 서로 짝지어지기 때문에 총 개수가 똑같기에 zip을 사용함
                    # th와 td의 열의 위치에 따라 어떤 동영상의 정보냐가 갈리기 때문에 enumerate와 zip을 동시에 사용함
                    th_list = []
                    for th_selector in th_selector_list:
                        # th 정보 가공
                        # 입력: ["작곡"] or ["작곡", "작사"] or ["작곡&편곡"] or ["작곡&편곡", "일러스트"]
                        # 이때 &/*로 두가지의 정보가 같이 있는 경우가 있는데 이는 아래에서 분리해야 됨
                        th_text_list = th_selector.css("::text").getall()
                        th_split_list = []
                        for th_text in th_text_list:
                            # 작곡&편곡, 노래/조교 같은 경우 분리
                            # 입력: ["작곡"] or ["작곡", "작사"] or ["작곡&편곡"] or ["작곡&편곡", "일러스트"]
                            text_split = re.split(r"[\/&\*]", th_text)
                            for t in text_split:
                                th_split_list.append(t.strip())
                        # 출력: [["작곡"]] or [["작곡"], ["작사"]] or [["작곡", "편곡"]] or [["작곡", "편곡"], ["일러스트"]]
                        th_list.append(th_split_list)

                    td_list = []
                    for td_selector in td_selector_list:
                        # td 정보 가공
                        # 인물 정보가 a태그와 기본 텍스트 정보있는 채로 혼재됨
                        # 다만 이들을 *::text와 getall로 가져오면 \n로 분리되어 있는 리스트를 가져올 수 있음
                        # 다만 \n의 위치가 일관적이지 않기에 이들을 join으로 합치고 다시 \n으로 분리함
                        td_text_list = td_selector.css("*::text").getall()
                        td_text_list = "".join(td_text_list).split("\n")
                        # 위의 과정을 거친 입력: [["인물1", ...]] or [["인물1", ... ], ["인물2", ...]]
                        # 다만 이 과정에서 th가 노래/조교, 코러스/조교인 경우 [["가수 / 인물", ...]]와 같은 형태가 됨
                        # 이는 아래에서 다시 정보를 분리해서 입력해야 될 필요가 있음
                        td_list.append([[text.strip() for text in td_text_list]])

                    for th_td_idx, (th_item_list, td_item_list) in enumerate(
                        zip(th_list, td_list)
                    ):
                        # th_item_list 입력: ["작곡"] or ["작곡", "편곡"]
                        # td_item_list 입력: [["인물1"]] or [["인물1", ... ], ["인물2", ... ]] or ["가수 / 인물", ... ]
                        for item_idx, th_item in enumerate(th_item_list):
                            # th_item 입력: "작곡"
                            # td_item 입력: ["인물1"], ["인물1", ... ] or ["가수 / 인물", ... ]
                            is_in_same = False
                            # th_item이 작곡, 작사에 해당하는 경우에는 모든 songInfo에 동일한 작곡, 작사 정보 추가
                            for table_info in table_info_same:
                                # 만약 th_item이 info에 있는 phrase에 해당한다면
                                # 해당하는 td_item을 모든 songInfo에 추가함
                                if th_item in table_info["phrase"]:
                                    for song_info in page_dict["songInfo"]:
                                        song_info[table_info["name"]] = td_item_list[
                                            th_td_idx
                                        ]
                                    is_in_same = True
                                    break

                            if is_in_same:
                                continue

                            # ["노래", "조교"], ["코러스", "조교"]와 같은 경우에 대한 조건
                            have_to_split_td = (
                                len(th_item_list) > 1 and "조교" in th_item_list
                            )

                            if have_to_split_td:
                                # "가수 / 인물"을 ["가수", "인물"]로 분리
                                # TODO: 혹시 더 일반적인 방법으로 분리가 가능한지 확인
                                # TODO: 이 코드의 원흉인 "싱 어 송"문서에 보컬로이드가 하츠네 미쿠Append처럼 기존의 표기 방식과 다른 방식이 있음
                                # 그에 대한 추가적인 처리 필요
                                td_item_split = [
                                    re.split(r"\s*\/\s*", td_item)
                                    for td_item in td_item_list[0]
                                ]
                                # 가수는 가수대로, 인물은 인물대로 분리
                                singer_list = [td_item[0] for td_item in td_item_split]
                                vocaloid_editor_list = [
                                    td_item[1] for td_item in td_item_split
                                ]

                            for table_info in table_info_diff:
                                # th_item 입력: "편곡" or ...
                                # td_item 입력: ["인물1", ... ] or ["가수 / 인물", ... ]
                                if th_item in table_info["phrase"]:
                                    # table이 2개인 경우에는 table의 번호로, 아닌 경우(열이 여러개인 경우)에는 th_td_idx로 정보를 넣을 위치를 결정함
                                    # TODO: 좀 더 일반적인 경우에도 대응할 수 있게 코드 고치기
                                    idx = (
                                        th_td_idx
                                        if len(table_list) == 1 and len(th_list) == 1
                                        else table_idx
                                    )
                                    # td_item이 2개 이상인 경우에는 현재 index에 해당하는 출처에 정보를 추가함
                                    if not have_to_split_td:
                                        page_dict["songInfo"][idx][
                                            table_info["name"]
                                        ] = td_item_list[item_idx]
                                    else:
                                        # 특이케이스라서 따로 처리
                                        if item_idx == 0:
                                            list_to_add = singer_list
                                        elif item_idx == 1:
                                            list_to_add = vocaloid_editor_list
                                        page_dict["songInfo"][idx][
                                            table_info["name"]
                                        ] = list_to_add

        # 표가 2개(이상)인 경우 두 표가 링크 이외에 전부 동일한지 확인
        # 이때 동일하다면 2개의 표를 1개로 합침
        # 이 경우 original_url은 원래 보카로 가사 위키처럼 니코동을 우선시함
        # 현재는 표가 2개 이상인 경우는 존재하지 않으므로 2개를 비교하는 코드만 작성
        if len(table_list) > 1:
            info_a = page_dict["songInfo"][0]
            info_b = page_dict["songInfo"][1]

            # 두 표의 정보가 동일한지 확인
            is_same = True
            if set(info_a.keys()) != set(info_b.keys()):
                is_same = False
            else:
                for key in info_a.keys():
                    if key != "originalUrl" and info_a[key] != info_b[key]:
                        is_same = False
                        break

            if is_same:
                # 두표가 같다면 니코동 링크가 있는 표를 우선시해서 정보를 합침
                if "nicovideo.jp" in info_a["originalUrl"]:
                    page_dict["songInfo"] = [info_a]
                else:
                    page_dict["songInfo"] = [info_b]

        # 가사 정보 추가
        lyrics_table_list = response.css(".wiki-content-table")
        # 가사 표가 2개 이상인 경우
        if len(lyrics_table_list) > 1:
            for lyrics_table in lyrics_table_list:
                # 가사 표가 2개가 동일한 가사 표인 경우가 있음
                # 이 경우 현재까지 발견된 오류는 처음 표시된 가사표가 끊겨있고 마지막 행이 비어있다는 공통점이 있음
                # 이를 통해서 잘못된 가사표를 걸러낼 수 있음
                # TODO: 추후 사이트가 수정된다면 잘못된 가사표를 걸러내는 다른 방법이 필요함
                last_lyrics = (
                    lyrics_table.css("tr:last-child").css("td::text, th::text").get()
                )
                if not last_lyrics:
                    lyrics_table_list = [lyrics_table]

        # 업데이트 된 가사표로 새로 가사를 크롤링함
        for lyrics_table in lyrics_table_list:
            lyrics = lyrics_table.css("tr").css("th::text, td::text").getall()
            # 이때 가사표가 2개 이상일 경우 동영상의 배치 순서 (왼>오)에 따라 가사도 배치되어 있다고 가정함
            # 동영상의 순서대로 가사를 배치함
            page_dict["lyrics"].append(lyrics)

        # pageUrl에서 제일 앞의 /를 뺀 이름으로 파일 저장
        with open(f"temp/{page_dict['pageUrl'][1:]}.json", "w", encoding="utf-8") as f:
            json.dump(page_dict, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    pass
