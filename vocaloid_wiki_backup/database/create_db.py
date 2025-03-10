from sqlmodel import (
    SQLModel,
    create_engine,
    Session,
    select,
)
from ..utils.text_types import TEXT_TABLE
from ..utils.db_types import Page, Song, Lyrics, StartCharType
from ..utils.types import PageInfo
from ..utils.parse_text import get_text_start_type
import os
import json


def data_to_str(data: list[str] | str | None) -> str | None:
    if data is None:
        return None
    if type(data) == str:
        return data
    return "\n".join(data)


sqlite_file_name = "vocaloid-lyrics-wiki.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)


def create_db_and_tables(delete_old_db: bool = False):
    if delete_old_db and os.path.exists(sqlite_file_name):
        os.remove(sqlite_file_name)
    SQLModel.metadata.create_all(engine)


def create_title():
    with Session(engine) as session:
        for text_type in TEXT_TABLE:
            start_char = StartCharType()
            start_char.startChar = text_type["char_enum"].value
            start_char.charName = text_type["name"]
            session.add(start_char)
            session.commit()


def create_page(data: PageInfo):
    with Session(engine) as session:
        page = Page()
        for key, value in data.items():
            if key == "songInfo" or key == "lyricsInfo":
                continue
            setattr(page, key, value)

        original_title = data.get("pageTitle")
        title_type = get_text_start_type(original_title)
        page.startCharId = title_type.value

        for song_info in data.get("songInfo"):
            song = Song()
            participants = {}
            for key, value in song_info.items():
                if key == "originalUrl" or key == "vocadbId":
                    setattr(song, key, value)
                else:
                    participants[key] = value
            # 참가자의 경우에는 json정보를 문자열로 변환해서 저장
            # TODO: 나중에 elastic search를 사용할 때 json으로 변환하기
            song.participants = json.dumps(participants, ensure_ascii=False)
            page.songs.append(song)

        for lyrics_info in data.get("lyricsInfo"):
            lyrics = Lyrics()
            for key, value in lyrics_info.items():
                setattr(lyrics, key, value)
            page.lyrics.append(lyrics)

        session.add(page)
        session.commit()
        session.refresh(page)


if __name__ == "__main__":
    pass
