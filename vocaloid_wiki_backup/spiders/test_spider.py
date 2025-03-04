import scrapy
from ..parser.songs import parse_song_page
from .wiki_class import LinkSpider
import json
from functools import partial


class TestParserSpider(LinkSpider):
    name = "test-parser"

    # 가사 예시들도 추가하기
    # 후리가나가 있는 경우
    # 한국어 가사인 경우
    urls = [
        "http://vocaro.wikidot.com/petals-sounds-associated-with-them",  # 일반적인 경우
        "http://vocaro.wikidot.com/raise",  # 원본 링크가 없는 경우
        "http://vocaro.wikidot.com/mosaic-roll",  # 2개의 곡과 1개의 표가 있는 경우
        "http://vocaro.wikidot.com/dance-robot-dance",  # 2개의 곡과 1개의 표가 있는 경우
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
        "http://vocaro.wikidot.com/letter-to-the-black-world",  # 가사에 footnote가 있는 경우
        # "http://vocaro.wikidot.com/alive",  # 제목이 중복이라서 링크가 있는 경우
    ]

    info_list = []

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url, partial(parse_song_page, self))

    def closed(self, reason):
        with open("test.json", mode="w", encoding="utf-8") as fp:
            json.dump(self.info_list, fp, ensure_ascii=False, indent=2)
        # self.log(self.info_list[0])
