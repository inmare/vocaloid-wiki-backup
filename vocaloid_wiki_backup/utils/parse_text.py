from enum import Enum, auto
from .parse_korean import decompose, character_is_korean
from .text_types import TEXT_TABLE, CharEnum


def get_text_start_type(text: str) -> CharEnum:
    """
    문자의 시작 글자가 어떤 타입인지 반환
    """
    first_char = ord(text[0])

    if ord("a") <= first_char <= ord("z") or ord("A") <= first_char <= ord("Z"):
        return CharEnum.latin

    if ord("0") <= first_char <= ord("9"):
        return CharEnum.number

    if character_is_korean(text[0]):
        decomposed_start_char = decompose(text[0])
        for table in TEXT_TABLE:
            if table["is_korean"] and decomposed_start_char[0] in table["start"]:
                return table["char_enum"]

    return CharEnum.special


if __name__ == "__main__":
    pass
