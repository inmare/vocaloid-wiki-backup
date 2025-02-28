import scrapy


class LinkSpider(scrapy.Spider):
    links: list[str] = []
    """
    일반적인 링크를 저장하는 list
    """
    error_links: list[str] = []
    """
    에러가 발생한 링크를 저장하는 list
    """
    debug_links: list[str] = []
    """
    디버깅용 링크를 저장하는 list
    """


if __name__ == "__main__":
    pass
