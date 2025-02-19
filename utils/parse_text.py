from enum import Enum, auto
from .parse_korean import decompose, character_is_korean


class TextType(Enum):
    h1 = 1  # ㄱ, ㄲ
    h2 = 2  # ㄴ
    h3 = 3  # ㄷ, ㄸ
    h4 = 4  # ㄹ
    h5 = 5  # ㅁ
    h6 = 6  # ㅂ
    h7 = 7  # ㅅ
    h8 = 8  # ㅇ
    h9 = 9  # ㅈ
    h10 = 10  # ㅊ
    h11 = 11  # ㅋ
    h12 = 12  # ㅌ
    h13 = 13  # ㅍ
    h14 = 14  # ㅎ
    latin = auto()  # 영어
    number = auto()  # 숫자
    special = auto()  # 특수문자


KOREAN_TABLE = [
    {
        "type": TextType.h1,
        "start": ["ㄱ", "ㄲ"],
    },
    {
        "type": TextType.h2,
        "start": ["ㄴ"],
    },
    {
        "type": TextType.h3,
        "start": ["ㄷ", "ㄸ"],
    },
    {
        "type": TextType.h4,
        "start": ["ㄹ"],
    },
    {
        "type": TextType.h5,
        "start": ["ㅁ"],
    },
    {
        "type": TextType.h6,
        "start": ["ㅂ", "ㅃ"],
    },
    {
        "type": TextType.h7,
        "start": ["ㅅ", "ㅆ"],
    },
    {
        "type": TextType.h8,
        "start": ["ㅇ"],
    },
    {
        "type": TextType.h9,
        "start": ["ㅈ", "ㅉ"],
    },
    {
        "type": TextType.h10,
        "start": ["ㅊ"],
    },
    {
        "type": TextType.h11,
        "start": ["ㅋ"],
    },
    {
        "type": TextType.h12,
        "start": ["ㅌ"],
    },
    {
        "type": TextType.h13,
        "start": ["ㅍ"],
    },
    {
        "type": TextType.h14,
        "start": ["ㅎ"],
    },
]


def get_text_start_type(text: str) -> TextType:
    """
    문자의 시작 글자가 어떤 타입인지 반환
    """
    first_char = ord(text[0])

    if ord("a") <= first_char <= ord("z") or ord("A") <= first_char <= ord("Z"):
        return TextType.latin

    if ord("0") <= first_char <= ord("9"):
        return TextType.number

    if character_is_korean(text[0]):
        decomposed_start_char = decompose(text[0])
        for table in KOREAN_TABLE:
            if decomposed_start_char[0] in table["start"]:
                return table["type"]

    return TextType.special


if __name__ == "__main__":
    pass
