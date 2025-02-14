from scrapy.selector import Selector
from typing import TypedDict
import os


class HtmlData(TypedDict):
    title: str
    content: str


def get_info(response, title):
    response = Selector(text=data["content"])
    table_list = response.css(".info-table")

    if not table_list:
        # table이 없을 경우 리다이렉트 링크를 가지고 있기 때문에 해당 링크들을 가져옴
        redirect_links = response.css("#page-content ul li a::attr(href)").getall()
        print(f"Song {title} has redirect links")
        for link in redirect_links:
            # 그리고 그 링크들을 타고 들어가서 동일한 작업을 진행함
            # response = get_response(link)
            # get_info(response, title)
            print(f"- {link}")
    else:
        # 원 제목 파싱
        original_title_text = table_list[0].css("tr:first-child *::text").getall()
        original_title = "".join(original_title_text).strip()

        if len(table_list) > 1:
            # table의 개수가 1개 이상인 경우 각 테이블에 대해서 정보를 파싱
            temp_info_list = []
            for table in table_list:
                info = parse_table(table)
                temp_info_list.append(info)

            # 그런 다음에 해당 정보를 서로 비교해서 중복되는 info를 제거하고 최종적인 info_list를 만듦
            info_list = []
            for temp_info in temp_info_list:
                pass
        else:
            # table의 개수가 1개인 경우 해당 table에 대해서만 정보를 파싱
            info_list = parse_table(table_list[0])

    # 가사 파싱


def parse_table(table_selector):
    # table의 tr 태그들을 가져옴
    # 이때 1번째 tr은 원 제목, 2번째 tr은 동영상 플레이어기에 3번째 tr부터 가져옴
    tr_list = table_selector.css("tr")[2:]


def parse_lyrics(lyrics_selector):
    return lyrics_selector


html_files = os.listdir("test/html")
html_data = []

for file in html_files:
    with open(f"test/html/{file}", "r", encoding="utf-8") as f:
        html_data.append(HtmlData(title=file, content=f.read()))

for data in html_data[2:3]:
    title = data["title"]
    print(f"Start parsing {title}")
    response = Selector(text=data["content"])
    get_info(response, title)
