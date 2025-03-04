from enum import Enum, auto
from typing import TypedDict


class CharEnum(Enum):
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


class CharType(TypedDict):
    char_enum: CharEnum
    is_korean: bool
    name: str
    start: list[str] | None


TEXT_TABLE: list[CharType] = [
    CharType(
        char_enum=CharEnum.h1,
        is_korean=True,
        name="ㄱ",
        start=["ㄱ", "ㄲ"],
    ),
    CharType(
        char_enum=CharEnum.h2,
        is_korean=True,
        name="ㄴ",
        start=["ㄴ"],
    ),
    CharType(
        char_enum=CharEnum.h3,
        is_korean=True,
        name="ㄷ",
        start=["ㄷ", "ㄸ"],
    ),
    CharType(
        char_enum=CharEnum.h4,
        is_korean=True,
        name="ㄹ",
        start=["ㄹ"],
    ),
    CharType(
        char_enum=CharEnum.h5,
        is_korean=True,
        name="ㅁ",
        start=["ㅁ"],
    ),
    CharType(
        char_enum=CharEnum.h6,
        is_korean=True,
        name="ㅂ",
        start=["ㅂ", "ㅃ"],
    ),
    CharType(
        char_enum=CharEnum.h7,
        is_korean=True,
        name="ㅅ",
        start=["ㅅ", "ㅆ"],
    ),
    CharType(
        char_enum=CharEnum.h8,
        is_korean=True,
        name="ㅇ",
        start=["ㅇ"],
    ),
    CharType(
        char_enum=CharEnum.h9,
        is_korean=True,
        name="ㅈ",
        start=["ㅈ", "ㅉ"],
    ),
    CharType(
        char_enum=CharEnum.h10,
        is_korean=True,
        name="ㅊ",
        start=["ㅊ"],
    ),
    CharType(
        char_enum=CharEnum.h11,
        is_korean=True,
        name="ㅋ",
        start=["ㅋ"],
    ),
    CharType(
        char_enum=CharEnum.h12,
        is_korean=True,
        name="ㅌ",
        start=["ㅌ"],
    ),
    CharType(
        char_enum=CharEnum.h13,
        is_korean=True,
        name="ㅍ",
        start=["ㅍ"],
    ),
    CharType(
        char_enum=CharEnum.h14,
        is_korean=True,
        name="ㅎ",
        start=["ㅎ"],
    ),
    CharType(
        char_enum=CharEnum.latin,
        is_korean=False,
        name="라틴문자",
        start=None,
    ),
    CharType(
        char_enum=CharEnum.number,
        is_korean=False,
        name="숫자",
        start=None,
    ),
    CharType(
        char_enum=CharEnum.special,
        is_korean=False,
        name="특수문자",
        start=None,
    ),
]
