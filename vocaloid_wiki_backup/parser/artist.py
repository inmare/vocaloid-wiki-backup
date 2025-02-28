from scrapy.http import response
from ..spiders.wiki_class import LinkSpider
from .songs import parse_song_redirects


def parse_artist_list(self: LinkSpider, response: response):
    """
    작곡가를 이름 순으로 분류한 서브페이지의 링크를 가져오는 함수
    """
    try:
        # TODO: 작곡가 목록을 데이터베이스에 추가하기
        # 작곡가 페이지는 각 작곡가의 페이지로 이동하는 서브 페이지가 있음
        artist_sub_links = response.css(".card-item a::attr(href)").getall()

        for sub_link in artist_sub_links:
            yield response.follow(
                sub_link, lambda response: parse_artist_sub_list(self, response)
            )
    except Exception as e:
        self.error_links.append(response.url)
        self.logger.error(f"{e} at {response.url}")


def parse_artist_sub_list(self: LinkSpider, response: response):
    """
    서브 페이지에서 작곡가 목록을 가져오는 함수
    """
    try:
        # 서브 페이지에서 작곡가 목록을 가져옴
        artist_links = response.css(
            "#page-content > ul li a:not(.newpage)::attr(href)"
        ).getall()

        for artist_link in artist_links:
            yield response.follow(
                artist_link, lambda response: parse_artist(self, response)
            )
    except Exception as e:
        self.error_links.append(response.url)
        self.logger.error(f"{e} at {response.url}")


def parse_artist(self: LinkSpider, response: response):
    """
    작곡가 페이지에서 곡 목록을 가져오는 함수
    """
    try:
        song_links = response.css(
            "#page-content .list-pages-box ul li a:not(.newpage)::attr(href)"
        ).getall()

        for song_link in song_links:
            if not song_link in self.links:
                yield response.follow(
                    song_link, lambda response: parse_song_redirects(self, response)
                )
    except Exception as e:
        self.error_links.append(response.url)
        self.logger.error(f"{e} at {response.url}")
