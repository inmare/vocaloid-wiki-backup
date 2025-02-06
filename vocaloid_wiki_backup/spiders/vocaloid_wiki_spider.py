import scrapy
import json
import os


class QuotesSpider(scrapy.Spider):
    name = "vocaloid-wiki"

    def start_requests(self):
        url = "http://vocaro.wikidot.com/allsongs"

        yield scrapy.Request(url, self.parse)

        # tag = getattr(self, "tag", None)
        # if tag is not None:
        #     url = url + "tag/" + tag
        # yield scrapy.Request(url, self.parse)

    def parse(self, response):
        card_css = "#page-content ul"
        pages = []

        for card in response.css(card_css):
            for link in card.css("li a"):
                page_url = link.css("::attr(href)").get()

                pages.append(page_url)

        pages.sort()

        for page in pages:
            yield response.follow(page, self.parse_song_page)

    def parse_song_page(self, response):
        song_css = "#page-content > p"
        songs = []

        for song in response.css(song_css):
            songs.append(
                {
                    "title": song.css("a::text").get(),
                    "url": song.css("a::attr(href)").get(),
                }
            )

        file_name = response.url.split("/")[-1]
        dir_name = file_name.split("-")[1]

        with open(f"json/{file_name}.json", "w", encoding="utf-8") as f:
            json.dump(songs, f, indent=2, ensure_ascii=False)

        if not os.path.exists(f"json/{dir_name}"):
            os.makedirs(f"json/{dir_name}")

        self.log(f"Saved file {file_name}")

        # if dir_name == "h1":
        for song in songs:
            yield response.follow(
                song["url"], self.parse_song, meta={"dir_name": dir_name}
            )

    def parse_song(self, response):
        info_dict = {
            "url": response.url,
        }

        page_title_css = "#page-title::text"
        page_title = response.css(page_title_css).get().strip()
        info_dict["page"] = page_title

        title_css = ".info-table th::text"
        title = response.css(title_css).get()
        info_dict["title"] = title

        info_css = ".info-table td a"
        info_order = ["songLink", "composer", "lyricist", "singer"]
        for idx, info in enumerate(response.css(info_css)):
            if idx == 0:
                text = info.attrib["href"]
            else:
                text = info.xpath("text()").get()

            info_dict[info_order[idx]] = text

        lyrics_css = ".wiki-content-table tr"
        lyrics = []
        for lyric in response.css(lyrics_css):
            if lyric.css("td"):
                lyrics.append(lyric.css("td::text").get())
            else:
                lyrics.append(lyric.css("th::text").get())

        info_dict["lyrics"] = lyrics

        dir_name = response.meta["dir_name"]

        with open(f"json/{dir_name}/{page_title}.json", "w", encoding="utf-8") as f:
            json.dump(info_dict, f, indent=2, ensure_ascii=False)

        self.log(f"Saved file {page_title}")


if __name__ == "__main__":
    pass
