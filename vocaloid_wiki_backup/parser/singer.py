from scrapy.http import response
from ..spiders.wiki_class import LinkSpider
from .songs import parse_song_redirects
from urllib.parse import urlparse


def parse_singer_list(self: LinkSpider, response: response):
    """
    가수 목록 페이지에서 가수 페이지로 넘어가는 링크를 가져오는 함수
    """
    # TODO: 이렇게 얻은 가수 목록들을 데이터 베이스에 저장하기
    try:
        singer_links = response.css(
            "#page-content > ul li a:not(.newpage)::attr(href)"
        ).getall()
        for singer_link in singer_links:
            yield response.follow(
                singer_link, lambda response: parse_singer_redirects(self, response)
            )
    except Exception as e:
        self.error_links.append(response.url)
        self.log(f"Error: {e} at {response.url}")


def parse_singer_redirects(self: LinkSpider, response: response):
    """
    가수 페이지에서 리다이렉트 여부를 파싱하는 함수\\
    파싱한 결과를 parse_singer에서 사용함
    """
    try:
        # 가수 페이지는 3가지의 경우가 있음
        # 1. 가수 페이지에 곡 목록이 있는 경우
        # 2. 곡 목록이 있지만 페이지가 여러개로 나뉘어 있는 경우 (IA)
        # 3. 곡을 제목에 따라 분리하는 서브 페이지 링크가 있는 경우 (하츠네 미쿠)

        # 서브 페이지 링크의 경우
        sub_links = response.css(".card-item a::attr(href)").getall()
        if sub_links:
            for sub_link in sub_links:
                yield response.follow(
                    sub_link, lambda response: parse_singer(self, response)
                )

        # 곡 목록이 여러 페이지로 나뉘어 있는 경우
        pager = response.css(".pager")
        if pager:
            pager_text = pager.css(".pager-no::text").get()
            total_pages = int(pager_text.split("/")[-1].strip())
            # 현재 페이지의 상대 url구하기 (/ia)
            relative_url = urlparse(response.url).path
            page_links = [f"{relative_url}/p/{i}" for i in range(1, total_pages + 1)]
            for page_link in page_links:
                yield response.follow(
                    page_link, lambda response: parse_singer(self, response)
                )
    except Exception as e:
        self.error_links.append(response.url)
        self.logger.error(f"{e} at {response.url}")


def parse_singer(self: LinkSpider, response: response):
    """
    가수 페이지에서 노래 목록을 가져오는 함수
    """
    # 예외적으로 몇몇 페이지에는 데모곡이 추가되어 있긴한데 그건 일단 넘어감
    # TODO: 가능하다면 각 페이지의 데모곡도 순회 할 수 있도록 하기
    # TODO: 기존의 links에 이미 링크가 존재하면 포함하지 않는 코드 추가

    try:
        list_pages_box = response.css(".list-pages-box")
        if list_pages_box:
            song_links = list_pages_box.css(
                "ul li a:not(.newpage)::attr(href)"
            ).getall()
        else:
            # 하츠네 미쿠 서브페이지의 경우 list_pages_box가 없음
            # 그렇기에 아래와 같은 선택자를 적용함
            # 추후 예외 발생시 수정될 수 있음
            song_links = response.css(
                "#page-content h1 + p a:not(.newpage)::attr(href)"
            ).getall()

        for song_link in song_links:
            # 위의 경우를 사용해서 링크를 가져오면 페이지 외부의 링크가 포함되는 경우가 있음
            # 그 경우를 제외하기 위해서 /로 시작하는 링크만 가져옴
            if song_link.startswith("/") and not song_link in self.links:
                yield response.follow(
                    song_link, lambda response: parse_song_redirects(self, response)
                )
    except Exception as e:
        self.error_links.append(response.url)
        self.logger.error(f"{e} at {response.url}")
