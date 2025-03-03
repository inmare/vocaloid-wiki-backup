import scrapy
from scrapy.http import response
from ..utils.types import PageInfo, SongInfo, LyricsInfo
from urllib.parse import urlparse


class SongParserSpider(scrapy.Spider):
    name = "song-parser"
    urls = [
        "http://vocaro.wikidot.com/coaddiction",  # 일반적인 경우
        "http://vocaro.wikidot.com/raise",  # 원본 링크가 없는 경우
        "http://vocaro.wikidot.com/mosaic-roll",  # 2개의 곡과 1개의 표가 있는 경우
        "http://vocaro.wikidot.com/dance-robot-dance",  # 2개의 곡과 1개의 표가 있는 경우
        # "http://vocaro.wikidot.com/alive",  # 제목이 중복이라서 링크가 있는 경우
        "http://vocaro.wikidot.com/brand-new-day",  # 2개의 정보 표가 존재하는 경우
        "http://vocaro.wikidot.com/telecaster-b-boy",  # 가사 표가 2개 이상인 경우
        "http://vocaro.wikidot.com/immature-discipline",  # 가사 표 2개 중 1개가 잘못된 경우
        "http://vocaro.wikidot.com/sing-a-song",  #  노래와 조교를 한 곳에 적어둔 경우
        "http://vocaro.wikidot.com/t-a-o",  # 기타 참여자라는 숨겨진 표가 존재
        "http://vocaro.wikidot.com/neppuu",  # 작사・작곡 형태
        "http://vocaro.wikidot.com/the-dream-that-girl-doll-dreamed",  # 참가자 사이에 문자가 포함됨
        "http://vocaro.wikidot.com/super-turkish-march-doomed",  # 원곡이 존재, 링크가 없음
        "http://vocaro.wikidot.com/momentary-drive",  # 출처 행이 없음
        "http://vocaro.wikidot.com/the-rain-clear-up-twice",  # 표에서 가사가 따로 나뉨
        "http://vocaro.wikidot.com/gekkou",  # 그냥 에러가 남
    ]
    info_list = []

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url, self.parse)

    def parse(self, response: response):
        page_info = PageInfo()

        relative_url = urlparse(response.url).path
        page_info["pageUrl"] = relative_url

        # 페이지 제목 파싱
        page_title = response.css("#page-title::text").get().strip()
        page_info["pageTitle"] = page_title

        table_list = response.css(".info-table")
        # 여러개의 table이 있을 수도 있지만 일단 처음 테이블만 가져옴
        table = table_list[0]

        tr_list = table.css("tr")
        # 원 제목 파싱
        original_title_text = table.css(".title-cell::text").get()
        page_info["originalPageTitle"] = original_title_text

        self.info_list.append(page_info)

        # original_title = "".join(original_title_text).strip()
        # page_info["originalTitle"] = original_title

        # if len(table_list) > 1:
        #     # table의 개수가 1개 이상인 경우 각 테이블에 대해서 정보를 파싱
        #     temp_info_list = []
        #     for table in table_list:
        #         info = parse_table(table)
        #         temp_info_list.append(info)

        #     # 표가 2개 이상인 경우는 없기에 2개에 대한 단순비교를 진행함
        #     # 그리고 두 표의 정보가 동일할 경우에는 니코동 링크가 있는 정보 1개만을 넣음
        #     info_list = []
        #     for temp_info in temp_info_list:
        #         # 표가 2개 이상인 경우에는 표를 나누지 않았기 때문에 각 리스트에 1개씩만의 song info만 존재함
        #         # 따라서 0번째 info를 가져와서 니코동 링크가 있는지 확인함
        #         if "nicovideo" in temp_info[0]["originalUrl"]:
        #             info_list.append(temp_info[0])
        #             break

        #     page_info["songInfo"] = info_list
        # else:
        #     # table의 개수가 1개인 경우 해당 table에 대해서만 정보를 파싱
        #     info_list = parse_table(table_list[0])
        #     page_info["songInfo"] = info_list

        # # 가사 파싱
        # lyrics_selector = response.css(".wiki-content-table")
        # page_info["lyricsInfo"] = parse_lyrics(response, lyrics_selector)

        # return page_info

    def closed(self, reason):
        self.log(self.info_list[0])
