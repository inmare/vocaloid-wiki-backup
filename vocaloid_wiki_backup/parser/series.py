from scrapy.http import response
from ..spiders.wiki_class import LinkSpider
from .songs import parse_song_redirects


def parse_series_list(self: LinkSpider, response: response):
    """
    앨범 링크 목록을 가져오는 함수
    """
    try:
        # 시리즈 목록을 가져옴
        series_links = response.css(
            "#page-content ul li a:not(.newpage)::attr(href)"
        ).getall()
        for series_link in series_links:
            yield response.follow(
                series_link, lambda response: parse_series(self, response)
            )
    except Exception as e:
        self.error_links.append(response.url)
        self.logger.error(f"{e} at {response.url}")


def parse_series(self: LinkSpider, response: response):
    """
    앨범에서 곡 목록을 가져오는 함수
    """
    # 앨범 페이지에서는 2가지의 형태로 곡 목록이 존재함

    # 1. 곡 형태로 목록이 있는 경우
    # 2. 곡 / 작곡가 형태로 존재하는 목록이 있는 경우
    # 앨범 페이지에서 곡 / 작곡가 형태로 존재하는 목록에서 곡 링크만 가져옴
    try:
        song_links = response.css(
            "#page-content ol li a:first-child:not(.newpage)::attr(href)"
        ).getall()

        for song_link in song_links:
            if not song_link in self.links:
                yield response.follow(
                    song_link, lambda response: parse_song_redirects(self, response)
                )
    except Exception as e:
        self.error_links.append(response.url)
        self.logger.error(f"{e} at {response.url}")
