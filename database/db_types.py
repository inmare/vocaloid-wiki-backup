from sqlmodel import SQLModel, Field, Relationship


class Page(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    pageUrl: str  # 페이지 URL, 상대 경로
    pageTitle: str  # 번역된 제목, 중복된 제목의 경우 작곡가가 제목에 포함될 수 있음
    originalPageTitle: str | None = Field(default=None)
    originalTitle: str  # 원 제목

    titleTypeId: int  # 제목 타입

    songs: list["Song"] = Relationship(back_populates="page")
    lyrics: list["Lyrics"] = Relationship(back_populates="page")


# TODO: scrapy의 데이터 타입과 자동으로 연동되게 하기?
class Song(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    page_id: int | None = Field(default=None, foreign_key="page.id")
    page: Page | None = Relationship(back_populates="songs")

    originalUrl: str | None = Field(default=None)  # 원곡 URL
    # 곡에 참여한 사람, 음합엔
    composer: str | None = Field(default=None)
    lyricist: str
    singer: str
    originalSong: str | None = Field(default=None)
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


class TitleType(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    titleType: str
