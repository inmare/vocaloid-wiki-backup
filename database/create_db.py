from sqlmodel import (
    SQLModel,
    create_engine,
    Session,
    select,
)
from utils.parse_text import TextType
from .db_types import Page, Song, Lyrics, TitleType
import os


def data_to_str(data: list[str] | str | None) -> str | None:
    if data is None:
        return None
    if type(data) == str:
        return data
    return "\n".join(data)


sqlite_file_name = "database/vocaloid-lyrics-wiki.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)


def create_db_and_tables(delete_old_db: bool = False):
    if delete_old_db and os.path.exists(sqlite_file_name):
        os.remove(sqlite_file_name)
    SQLModel.metadata.create_all(engine)


def create_title():
    for text_enum in TextType:
        with Session(engine) as session:
            title_type = TitleType()
            title_type.titleType = text_enum.name
            session.add(title_type)
            session.commit()


def create_page(data: dict):
    with Session(engine) as session:
        page = Page()
        for key, value in data.items():
            if key == "songInfo" or key == "lyricsInfo":
                continue
            setattr(page, key, value)

        for song_info in data.get("songInfo"):
            song = Song()
            for key, value in song_info.items():
                setattr(song, key, data_to_str(value))
            page.songs.append(song)

        for lyrics_info in data.get("lyricsInfo"):
            lyrics = Lyrics()
            for key, value in lyrics_info.items():
                setattr(lyrics, key, data_to_str(value))
            page.lyrics.append(lyrics)

        session.add(page)
        session.commit()
        session.refresh(page)


if __name__ == "__main__":
    pass
