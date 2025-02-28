from scrapy.http import response
from ..spiders.wiki_class import LinkSpider
from .songs import parse_song_redirects


def parse_allsong_list(self: LinkSpider, response: response):
    """
    모든 노래 모음에서 서브 페이지의 링크를 가져오는 함수
    """
    try:
        title_links = response.css(".card-item > a::attr(href)").getall()

        for title_link in title_links:
            yield response.follow(
                title_link, lambda response: parse_title_list(self, response)
            )
    except Exception as e:
        self.error_links.append(response.url)
        self.logger.error(f"{e} at {response.url}")


def parse_title_list(self: LinkSpider, response: response):
    """
    모든 노래 모음의 서브 페이지에서 각 노래의 링크를 가져오는 함수
    """
    try:
        # 이때 .newpage 클래스는 존재하지 않는 페이지에 붙기 때문에 제외함
        song_links = response.css(
            "#page-content > p > a:not(.newpage)::attr(href)"
        ).getall()

        for song_link in song_links:
            if not song_link in self.links:
                yield response.follow(
                    song_link, lambda response: parse_song_redirects(self, response)
                )
    except Exception as e:
        self.error_links.append(response.url)
        self.logger.error(f"{e} at {response.url}")
