import scrapy
import json
from functools import partial
from ..parser.allsongs import parse_allsong_list
from ..parser.singer import parse_singer_list
from ..parser.artist import parse_artist_list
from ..parser.series import parse_series_list
from ..parser.numbers import parse_numbers_list
from .wiki_class import LinkSpider


# TODO: 중복 링크 페이지에 대한 처리 추가하기
class WholeLinkSpider(LinkSpider):
    name = "whole-links"
    use_existing_database = False

    def start_requests(self):
        # 디버깅 용도로 기존의 whole-links.json파일의 데이터를 사용할 때
        if self.use_existing_database:
            with open(f"test/test_data/{self.name}.json", "r", encoding="utf-8") as f:
                self.links = json.load(f)

        urls = [
            "http://vocaro.wikidot.com/allsongs",  # 전체 가사 링크
            "http://vocaro.wikidot.com/singers",  # 음성 합성 엔진 링크
            "http://vocaro.wikidot.com/artist",  # 작곡가 링크
            "http://vocaro.wikidot.com/series",  # 시리즈 링크
            "http://vocaro.wikidot.com/numbers",  # 인원수 링크
        ]

        funcs = [
            parse_allsong_list,
            parse_singer_list,
            parse_artist_list,
            parse_series_list,
            parse_numbers_list,
        ]

        for url, func in zip(urls, funcs):
            yield scrapy.Request(url, partial(func, self))

    def closed(self, reason):
        self.log(f"{len(self.links)}개의 곡들을 발견했습니다.")
        self.log(f"{len(self.debug_links)}개의 누락된 곡들을 발견했습니다.")
        with open(f"test/test_data/{self.name}.json", "w", encoding="utf-8") as f:
            json.dump(self.links, f, indent=2)
        with open(f"test/test_data/error-{self.name}.json", "w", encoding="utf-8") as f:
            json.dump(self.error_links, f, indent=2)
        with open(f"test/test_data/debug-{self.name}.json", "w", encoding="utf-8") as f:
            json.dump(self.debug_links, f, indent=2)


if __name__ == "__main__":
    pass
