from scrapy.http import response
from ..spiders.wiki_class import LinkSpider
from .songs import parse_song_redirects
from urllib.parse import urlparse


def parse_numbers_list(self: LinkSpider, response: response):
    """
    인원 수 목록에서 pager에 따라 처리를 분리하하는 함수
    """
    try:
        # 듀엣의 경우 pager가 있으므로 이 경우에는 따로 처리함
        pager = response.css(".pager")
        pager_text = pager.css(".pager-no::text").get()
        total_pages = int(pager_text.split("/")[-1].strip())
        relative_url = urlparse(response.url).path
        page_links = [f"{relative_url}/p/{i}" for i in range(1, total_pages + 1)]

        for page_link in page_links:
            yield response.follow(
                page_link, lambda response: parse_numbers(self, response)
            )

        # 듀엣이 아닌 나머지 곡들 처리
        song_links = response.css(
            "#page-content .list-pages-box:not(:first-child) a:not(.newpage)::attr(href)"
        ).getall()

        for song_link in song_links:
            if not song_link in self.links:
                yield response.follow(
                    song_link, lambda response: parse_song_redirects(self, response)
                )
    except Exception as e:
        self.error_links.append(response.url)
        self.logger.error(f"{e} at {response.url}")


def parse_numbers(self: LinkSpider, response: response):
    """
    인원 수 목록에서 노래를 분리하는 함수
    """
    try:
        song_links = response.css(
            f"#page-content .list-pages-box:first-child a:not(.newpage)::attr(href)"
        ).getall()

        for song_link in song_links:
            yield response.follow(
                song_link, lambda response: parse_song_redirects(self, response)
            )
    except Exception as e:
        self.error_links.append(response.url)
        self.logger.error(f"{e} at {response.url}")
