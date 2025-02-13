import scrapy
from urllib.parse import urlparse


class VocaloidWikiSpider(scrapy.Spider):
    name = "sample-page"

    def start_requests(self):
        urls = [
            "http://vocaro.wikidot.com/coaddiction",
            "http://vocaro.wikidot.com/raise",
            "http://vocaro.wikidot.com/mosaic-roll",
            "http://vocaro.wikidot.com/dance-robot-dance",
            "http://vocaro.wikidot.com/alive",
            "http://vocaro.wikidot.com/brand-new-day",
            "http://vocaro.wikidot.com/telecaster-b-boy",
            "http://vocaro.wikidot.com/immature-discipline",
            "http://vocaro.wikidot.com/sing-a-song",
        ]

        for url in urls:
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        url_parsed = urlparse(response.url)
        file_name = url_parsed.path.split("/")[-1]
        with open(f"test/html/{file_name}.html", "w", encoding="utf-8") as f:
            f.write(response.text)


if __name__ == "__main__":
    pass
