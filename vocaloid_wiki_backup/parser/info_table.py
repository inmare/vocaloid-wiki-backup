from typing import TypedDict
from urllib.parse import urlparse
import re
from ..utils.types import SongInfo, TERM_DICT


class HtmlData(TypedDict):
    title: str
    content: str


def get_th_info(th_text: str):
    th_info = []
    for song_term in TERM_DICT:
        terms = song_term["term"]
        for t in terms:
            if t in th_text:
                th_info.append(t)
                break
    return th_info


def find_meta_from_name(nickname: str):
    return list(filter(lambda term: term["nickname"] == nickname, TERM_DICT))[0]


def put_data_to_info(
    info_list, current_info, phrase_text, data, has_multiple_url, has_single_pair
):
    for meta in TERM_DICT:
        if phrase_text in meta["term"]:
            if meta["mustSame"] or (has_multiple_url and has_single_pair):
                for info in info_list:
                    info[meta["nickname"]] = data
            else:
                current_info[meta["nickname"]] = data
            break


def parse_table(table_selector):
    info_list = []

    # table의 tr 태그들을 가져옴
    # 이때 1번째 tr은 원 제목, 2번째 tr은 동영상 플레이어기에 3번째 tr부터 가져옴
    tr_list = table_selector.css("tr")

    # 일반적인 경우 2번째 tr에 출처를 담은 링크가 있지만 없는 경우도 있음
    # 이 경우에는 info_idx를 2로 설정함
    info_idx = 3
    third_tr_th_text = tr_list[2].css("th *::text").get()
    if third_tr_th_text == "출처":
        # 원본 URL 파싱
        original_url_list = tr_list[2].css("a::attr(href)").getall()
        # logging.debug(f"Original URL: {original_url_list}")
    else:
        info_idx = 2
        # TODO: 현재는 니코동 플레이어에만 대응되게 해놨지만 나중에 다른 플레이어도 대응할 수 있도록 수정 필요
        player_links = tr_list[1].css(".embed-video-wrap iframe::attr(src)").getall()
        original_url_list = []
        for player_link in player_links:
            parsed_link = urlparse(player_link).path
            original_url_list.append("https://www.nicovideo.jp" + parsed_link)

    for original_url in original_url_list:
        if original_url == "":
            info = SongInfo(originalUrl=None)
        else:
            info = SongInfo(originalUrl=original_url)
        info_list.append(info)

    has_multiple_url = len(original_url_list) > 1

    # 만약 원본 url이 2개 이상이라면 그 밑의 tr에서 정보가 나누어질 때 맞는 위치에 넣어야 함
    # 이때 위치는 원본 url 배치 순서를 따름
    for tr in tr_list[info_idx:]:
        # 일부 문서의 접을 수 있는 블럭에 해당하는 tr이 있는지 확인함
        # 해당 tr은 아무런 내용도 없으므로 스킵함
        is_collapsible_tr = tr.css(".collapsible-block").get()
        if is_collapsible_tr:
            continue

        # 각 tr에서 th와 td를 모두 가져옴
        th_selector_list = tr.css("th")
        td_selector_list = tr.css("td")

        selector_pair = zip(th_selector_list, td_selector_list)
        has_single_pair = len(th_selector_list) == 1

        for pair_idx, (th_selector, td_selector) in enumerate(selector_pair):
            current_info = info_list[pair_idx]

            # th와 td를 한 묶음으로 가져온 다음에 각각의 text를 가져옴
            th_text = th_selector.css("*::text").get()
            td_text_list = td_selector.css("*::text").getall()
            # 줄바꿈 문자나 다른 문자들로 td가 나뉘어져 있는 걸 분리함
            # TODO: ×의 경우 히토시즈쿠 × 야마△의 경우를 위한 것으로 추후 수정가능능
            td_text_list = re.split(r"\s*[\n×]\s*", "".join(td_text_list).strip())
            # logging.debug(f"{th_text}: {td_text_list}")

            # th가 여러 개의 정보를 가지고 있는지 확인
            # 작사작곡처럼 붙어있는 경우 추가
            # TODO: 만약 나중에 다른 경우가 생긴다면 추가해야 함
            th_text_list = get_th_info(th_text)
            # has_multiple_th = re.search(r"[&*\/s・]", th_text) or th_text == "작사작곡"
            has_multiple_th = len(th_text_list) > 1
            if has_multiple_th:
                # 만약 그렇다면 th를 분리해서 list로 만듦
                # th_text_list = re.split(r"[&*\/・]", th_text)

                # th가 노래/조교, 코러스/조교일 경우 td에도 음합엔 / 조교자의 형태로 여러가지 정보가 있음
                # 이를 확인하기 위한 과정
                # 조교에 해당하는 phrase를 찾음
                phrase_vocaloid_editor = find_meta_from_name("조교")["term"]
                # 조교가 th에 있는지 확인
                has_vocaloid_editor_phrase = any(
                    map(lambda phrase: phrase in th_text_list, phrase_vocaloid_editor)
                )

                # td를 분리해야 하는경우 분리해서 각각의 정보를 만듦
                if has_vocaloid_editor_phrase:
                    # td가 여러 개인 경우는 (노래, 코러스)/조교 뿐이므로 정보를 2개의 list로 분리
                    singer_list = []
                    vocaloid_editor_list = []

                    for text in td_text_list:
                        td_split = re.split(r"\s*\/\s*", text)
                        singer_list.append(td_split[0])
                        vocaloid_editor_list.append(td_split[1])

                    name_singer = find_meta_from_name("노래")["name"]
                    name_vocaloid_editor = find_meta_from_name("조교")["name"]

                    # 겹치는 이름 제거
                    current_info[name_singer] = list(set(singer_list))
                    current_info[name_vocaloid_editor] = list(set(vocaloid_editor_list))
                else:
                    # td가 여러개가 아닌 경우 th 리스트의 th들에 기존 정보를 넣음
                    for th_text_item in th_text_list:
                        put_data_to_info(
                            info_list,
                            current_info,
                            th_text_item,
                            td_text_list,
                            has_multiple_url,
                            has_single_pair,
                        )
            else:
                # th가 여러개가 아닌 경우 그냥 th와 td를 비교해서 정보를 넣음
                put_data_to_info(
                    info_list,
                    current_info,
                    th_text,
                    td_text_list,
                    has_multiple_url,
                    has_single_pair,
                )

    return info_list


if __name__ == "__main__":
    pass
