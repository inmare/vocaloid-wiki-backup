from ..utils.types import LyricsInfo
from lxml import html, etree


def remove_html_attrib(html_string: str):
    tree = html.fromstring(html_string)

    # 모든 태그에서 속성을 제거
    for element in tree.iter():
        element.attrib.clear()

    return etree.tostring(tree, encoding="unicode", method="html")


def parse_lyrics(response):
    lyrics_selector = response.css(".wiki-content-table")

    # 가사 표가 2개 이상인 경우
    if len(lyrics_selector) > 1:
        for lyrics_table in lyrics_selector:
            # 가사 표가 2개가 동일한 가사 표인 경우가 있음
            # 이 경우 현재까지 발견된 오류는 처음 표시된 가사표가 끊겨있고 마지막 행이 비어있다는 공통점이 있음
            # 이를 통해서 잘못된 가사표를 걸러낼 수 있음
            # TODO: 추후 사이트가 수정된다면 잘못된 가사표를 걸러내는 다른 방법이 필요함
            last_lyrics = "".join(
                lyrics_table.css("tr:last-child *::text").getall()
            ).strip()
            if not last_lyrics:
                lyrics_selector = [lyrics_table]

    lyrics_info_list: list[LyricsInfo] = []

    # 업데이트 된 가사표로 새로 가사를 크롤링함
    for lyrics_table in lyrics_selector:
        lyrics_tr = lyrics_table.css("tr")
        lyrics = []
        # the-rain-clear-up-twice의 경우처럼 한 행에서 표가 2개로 나뉘어지는 경우가 있음
        # 그런 경우를 위해서 임시로 for문을 돌면서 가사를 띄어쓰기와 함께 모아주는 코드 작성
        # TODO: sup 태그를 이용해서 가사가 나뉘어지는 경우에 대한 처리가 필요함
        for tr in lyrics_tr:
            tr_text = tr.css("th::text, td::text, sup::text").getall()
            lyrics_text = ""
            for text in tr_text:
                lyrics_text += text + " "
            # 문서들의 일본어 가사에 전각 공백과 반각 공백이 혼재되어 있음
            lyrics.append(lyrics_text.strip())

        lyrics_html = remove_html_attrib(lyrics_table.get())
        # 이때 가사표가 2개 이상일 경우 동영상의 배치 순서 (왼>오)에 따라 가사도 배치되어 있다고 가정함
        # 동영상의 순서대로 가사를 배치함
        lyrics_info = LyricsInfo(lyrics="\n".join(lyrics), lyricsHtml=lyrics_html)
        lyrics_info_list.append(lyrics_info)

    footnotes_html = response.css(".footnotes-footer").get()
    if footnotes_html:
        footnotes_raw_html = remove_html_attrib(footnotes_html)
        for lyrics_info in lyrics_info_list:
            lyrics_info["footerHtml"] = footnotes_raw_html

    table_wrap = response.css(".table-wrap")
    if table_wrap:
        # logging.debug(table_wrap.css("h2 span"))
        lyrics_versions = table_wrap.css("h2 span::text").getall()
        for idx, version in enumerate(lyrics_versions):
            lyrics_info_list[idx]["version"] = version

    return lyrics_info_list
