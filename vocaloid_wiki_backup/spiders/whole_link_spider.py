import scrapy
import json


class WholeLinkSpider(scrapy.Spider):
    name = "whole-links"
    whole_links = []

    def start_requests(self):
        urls = [
            "http://vocaro.wikidot.com/allsongs",  # 전체 가사 링크
            "http://vocaro.wikidot.com/singers",  # 음성 합성 엔진 링크
            "http://vocaro.wikidot.com/artist",  # 작곡가 링크
            "http://vocaro.wikidot.com/series",  # 시리즈 링크
            "http://vocaro.wikidot.com/numbers",  # 인원수 링크
        ]

        funcs = [
            self.parse_allsong_list,
            self.parse_singer_list,
            self.parse_artist_list,
            self.parse_series_list,
            self.parse_numbers,
        ]

        for url, func in zip(urls, funcs):
            yield scrapy.Request(url, func)

    def parse_allsong_list(self, response):
        # 모든 노래 모음을 파싱하는 페이지
        # ㄱ, ㄴ, ㄷ, ... 순으로 가사 페이지로 이동
        title_links = response.css(".card-item a::attr(href)").getall()

        for title_link in title_links:
            yield response.follow(title_link, self.parse_title_list)
            # yield scrapy.Request(sub_link, self.parse_song)

    def parse_title_list(self, response):
        # ㄱ, ㄴ, ㄷ... 페이지에서 각 노래의 링크를 가져옴
        # 이때 .newpage 클래스는 존재하지 않는 페이지에 붙기 때문에 제외함
        song_links = response.css(
            "#page-content > p a:not(.newpage)::attr(href)"
        ).getall()
        for song_link in song_links:
            if song_link not in self.whole_links:
                # 링크가 없을 경우에만 곡 목록에 링크 추가
                self.whole_links.append(song_link)
                # yield scrapy.Request(song_link, self.parse_song)

    def parse_singer_list(self, response):
        # 각 음성 합성 엔진의 페이지를 먼저 얻음
        singer_links = response.css("#page-content > ul li a::attr(href)").getall()
        for singer_link in singer_links:
            yield response.follow(singer_link, self.parse_singer)

    def parse_singer(self, response, meta={"rediredted": False}):
        # 만약 페이지에 pager클래스가 있다면 여러 페이지에 걸쳐서 곡이 있다는 이야기임
        # 따라서 해당 페이지를 순차적으로 순회해야 됨
        pager = response.css(".pager")
        if pager and not response.meta.get("redirected"):
            pager_no_text = pager.css(".pager-no::text").get()
            # 페이지 1 / 2의5 텍스트에서 전체 페이지 수 구하기
            pager_no = int(pager_no_text.split("/")[-1].strip())
            # 현재 페이지의 url구하기
            relative_url = response.url.split("/")[-1]
            for i in range(1, pager_no + 1):
                # 리다이렉트 되었음을 meta로 알려줌
                yield response.follow(
                    f"/{relative_url}/p/{i}",
                    self.parse_singer,
                    meta={"redirected": True},
                )
        else:
            # 음성 합성 엔진의 페이지에는 공통적으로 수록곡의 list 형태로 노래 목록이 있음
            # 예외적으로 몇몇 페이지에는 데모곡이 추가되어 있긴한데 그건 일단 넘어감
            # TODO: 가능하다면 각 페이지의 데모곡도 순회 할 수 있도록 하기
            song_links = response.css(
                "#page-content .list-pages-box ul li a:not(.newpage)::attr(href)"
            ).getall()
            for song_link in song_links:
                if song_link not in self.whole_links:
                    self.whole_links.append(song_link)

    def parse_artist_list(self, response):
        # 작곡가 페이지는 각 작곡가의 페이지로 이동하는 서브 페이지가 있음
        artist_sub_links = response.css(".card-item a::attr(href)").getall()
        for sub_link in artist_sub_links:
            yield response.follow(sub_link, self.parse_artist_sub_list)

    def parse_artist_sub_list(self, response):
        # 서브 페이지에서 작곡가 목록을 가져옴
        artist_links = response.css(
            "#page-content > ul li a:not(.newpage)::attr(href)"
        ).getall()
        for artist_link in artist_links:
            yield response.follow(artist_link, self.parse_artist)

    def parse_artist(self, response):
        song_links = response.css(
            "#page-content > ul li a:not(.newpage)::attr(href)"
        ).getall()
        for song_link in song_links:
            if song_link not in self.whole_links:
                self.whole_links.append(song_link)
                # yield scrapy.Request(song_link, self.parse_song)

    def parse_series_list(self, response):
        # 시리즈 목록을 가져옴
        series_links = response.css(
            "#page-content ul li a:not(.newpage)::attr(href)"
        ).getall()
        for series_link in series_links:
            yield response.follow(series_link, self.parse_series)

    def parse_series(self, response):
        # 시리즈 페이지에서 곡 / 작곡가 형태로 존재하는 목록에서 곡 링크만 가져옴
        song_links = response.css(
            "ol li a:first-child:not(.newpage)::attr(href)"
        ).getall()

        for song_link in song_links:
            if song_link not in self.whole_links:
                self.whole_links.append(song_link)
                # yield scrapy.Request(song_link, self.parse_song)

    def parse_numbers(self, response, meta={"redirect": False}):
        # 인원수 목록을 가져옴
        # 이때 듀엣곡의 경우에는 pager클래스가 존재하므로 이 경우는 따로 처리해줘야 함
        pager = response.css(".pager")
        if pager and not response.meta.get("redirected"):
            pager_no_text = pager.css(".pager-no::text").get()
            # 페이지 1 / 2의 텍스트에서 전체 페이지 수 구하기
            pager_no = int(pager_no_text.split("/")[-1].strip())
            # 현재 페이지의 url구하기
            relative_url = response.url.split("/")[-1]
            for i in range(1, pager_no + 1):
                # 리다이렉트 되었음을 meta로 알려줌
                yield response.follow(
                    f"/{relative_url}/p/{i}",
                    self.parse_numbers,
                    meta={"redirected": True},
                )
        else:
            if response.meta.get("redirect"):
                # 리다이렉트 되었다면 듀엣 페이지의 값만을 가져옴
                song_links = response.css(
                    "#page-content .list-pages-box:first-child a:not(.newpage)::attr(href)"
                ).getall()
            else:
                # 그 외의 경우에는 나머지의 값을 전부 가져옴
                song_links = response.css(
                    "#page-content .list-pages-box:not(:first-child) a:not(.newpage)::attr(href)"
                ).getall()

            for song_link in song_links:
                if song_link not in self.whole_links:
                    self.whole_links.append(song_link)
                    # yield scrapy.Request(numbers_link, self.parse_song)

    def closed(self, reason):
        self.log(len(self.whole_links) + "개의 곡들을 발견했습니다.")
        with open("test/test_data/whole_links.json", "w", encoding="utf-8") as f:
            json.dump(self.whole_links, f, indent=4)


if __name__ == "__main__":
    pass
