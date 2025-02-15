from sqlmodel import (
    Field,
    SQLModel,
    Relationship,
    create_engine,
    Session,
    select,
)
import json
import os


class Page(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    pageUrl: str  # 페이지 URL, 상대 경로
    pageTitle: str  # 번역된 제목, 중복된 제목의 경우 작곡가가 제목에 포함될 수 있음
    originalPageTitle: str | None = Field(default=None)
    originalTitle: str  # 원 제목

    songs: list["Song"] = Relationship(back_populates="page")
    lyrics: list["Lyrics"] = Relationship(back_populates="page")


# TODO: scrapy의 데이터 타입과 자동으로 연동되게 하기?
class Song(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    page_id: int | None = Field(default=None, foreign_key="page.id")
    page: Page | None = Relationship(back_populates="songs")

    originalUrl: str | None = Field(default=None)  # 원곡 URL
    # 곡에 참여한 사람, 음합엔
    composer: str
    lyricist: str
    singer: str
    arranger: str | None = Field(default=None)
    chorus: str | None = Field(default=None)
    vocaloidEditor: str | None = Field(default=None)
    illustrator: str | None = Field(default=None)
    videoProducer: str | None = Field(default=None)
    engineering: str | None = Field(default=None)
    mixing: str | None = Field(default=None)
    mastering: str | None = Field(default=None)
    pianist: str | None = Field(default=None)
    guitarist: str | None = Field(default=None)
    bassist: str | None = Field(default=None)
    drummer: str | None = Field(default=None)
    trumpeter: str | None = Field(default=None)
    trombonist: str | None = Field(default=None)
    altoSaxophonist: str | None = Field(default=None)
    playerEtc: str | None = Field(default=None)


class Lyrics(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    page_id: int | None = Field(default=None, foreign_key="page.id")
    page: Page | None = Relationship(back_populates="lyrics")

    lyrics: str  # 가사
    version: str | None = Field(default=None)


def data_to_str(data: list[str] | str | None) -> str | None:
    if data is None:
        return None
    if type(data) == str:
        return data
    return "\n".join(data)


sqlite_file_name = "database/vocaloid-lyrics-wiki.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)


def create_db_and_tables():
    if os.path.exists(sqlite_file_name):
        os.remove(sqlite_file_name)
    SQLModel.metadata.create_all(engine)


def create_page(data: dict):
    with Session(engine) as session:
        page = Page(
            pageUrl=data.get("pageUrl"),
            pageTitle=data.get("pageTitle"),
            originalPageTitle=data.get("originalPageTitle"),
            originalTitle=data.get("originalTitle"),
        )

        for song_info in data.get("songInfo"):
            song = Song(
                originalUrl=data_to_str(song_info.get("originalUrl")),
                composer=data_to_str(song_info.get("composer")),
                lyricist=data_to_str(song_info.get("lyricist")),
                singer=data_to_str(song_info.get("singer")),
                arranger=data_to_str(song_info.get("arranger")),
                chorus=data_to_str(song_info.get("chorus")),
                vocaloidEditor=data_to_str(song_info.get("vocaloidEditor")),
                illustrator=data_to_str(song_info.get("illustrator")),
                videoProducer=data_to_str(song_info.get("videoProducer")),
                engineering=data_to_str(song_info.get("engineering")),
                mixing=data_to_str(song_info.get("mixing")),
                mastering=data_to_str(song_info.get("mastering")),
                pianist=data_to_str(song_info.get("pianist")),
                guitarist=data_to_str(song_info.get("guitarist")),
                bassist=data_to_str(song_info.get("bassist")),
                drummer=data_to_str(song_info.get("drummer")),
                trumpeter=data_to_str(song_info.get("trumpeter")),
                trombonist=data_to_str(song_info.get("trombonist")),
                altoSaxophonist=data_to_str(song_info.get("altoSaxophonist")),
                playerEtc=data_to_str(song_info.get("playerEtc")),
            )
            page.songs.append(song)

        for lyrics_info in data.get("lyricsInfo"):
            lyrics = Lyrics(
                lyrics=data_to_str(lyrics_info.get("lyrics")),
                version=data_to_str(lyrics_info.get("version")),
            )
            page.lyrics.append(lyrics)

        session.add(page)
        session.commit()
        session.refresh(page)


def find_page(page_url: str) -> Page:
    with Session(engine) as session:
        statement = select(Page).where(Page.pageUrl == page_url)
        page = session.exec(statement).first()
        print(page.songs)
        print(page.lyrics)


if __name__ == "__main__":
    json_list = os.listdir("json/temp")
    data_list = []
    for json_file in json_list:
        with open(f"json/temp/{json_file}", "r", encoding="utf-8") as f:
            data = json.load(f)
            data_list.append(data)

    create_db_and_tables()
    for data in data_list:
        create_page(data)
    # 노래 검색
    page = find_page("/telecaster-b-boy")
