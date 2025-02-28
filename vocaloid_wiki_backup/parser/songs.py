from scrapy.http import response
from ..spiders.wiki_class import LinkSpider
from urllib.parse import urlparse


def parse_song_redirects(self: LinkSpider, response: response):
    """
    곡 페이지의 리다이렉트 여부를 파싱하는 함수\\
    파싱한 결과를 LinkSpider.links에 추가함
    """
    try:
        # TODO: 기존의 links에 이미 링크가 존재하면 포함하지 않는 코드 추가

        # 곡 정보를 담은 table이 있는지 확인
        info_table_list = response.css(".info-table")
        if not info_table_list:
            redirect_links = response.css(
                "#page-content ul li a:not(.newpage)::attr(href)"
            ).getall()

            for redirect_link in redirect_links:
                # 리다이렉트 링크가 곡 뿐만 아니라 앨범 등을 가리키는 경우도 있음
                # 해당 경우에는 링크에 :이 들어감을 이용해서 제외함
                if ":" not in redirect_link and redirect_link not in self.links:
                    self.links.append(redirect_link)
                    self.debug_links.append(redirect_link)
        else:
            # 만약 정보 테이블이 있으면 곡의 상대 url을 links에 추가함
            relative_path = urlparse(response.url).path
            if relative_path not in self.links:
                self.links.append(relative_path)
                self.debug_links.append(relative_path)
    except Exception as e:
        self.error_links.append(response.url)
        self.logger.error(f"{e} at {response.url}")
