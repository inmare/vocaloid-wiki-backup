from sqlmodel import SQLModel, Field, Relationship

# 데이터베이스의 클래스 이름은 json으로 주로 데이터 교환이 이루어진다는 것을 감안해서 camel case로 작성함


class Page(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    pageUrl: str  # 페이지 URL, 상대 경로
    pageTitle: str  # 번역된 제목, 중복된 제목의 경우 작곡가가 제목에 포함될 수 있음
    originalPageTitle: str | None = Field(default=None)
    originalTitle: str  # 원 제목

    startCharId: int  # 제목 타입

    songs: list["Song"] = Relationship(back_populates="page")
    lyrics: list["Lyrics"] = Relationship(back_populates="page")


# TODO: scrapy의 데이터 타입과 자동으로 연동되게 하기?
class Song(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    pageId: int | None = Field(default=None, foreign_key="page.id")
    page: Page | None = Relationship(back_populates="songs")

    originalUrl: str | None = Field(default=None)  # 원곡 URL
    vocadbId: int | None  # vocadb id

    # 곡에 참여한 사람, 음합엔
    participants: str


class Lyrics(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    pageId: int | None = Field(default=None, foreign_key="page.id")
    page: Page | None = Relationship(back_populates="lyrics")

    lyrics: str  # 가사, 추후에 위키 문법으로 고치기
    lyricsHtml: str  # 가사, HTML
    footerHtml: str | None = Field(default=None)

    # lyricsRaw: str | None = Field(default=None)  # 가사, 원본
    version: str | None = Field(default=None)


class StartCharType(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    startChar: str  # latin, special, h1... 같은 타입
    charName: str  # 라틴 문자, 특수 문자, ㄱ... 등등 해당 타입을 나타내는 이름
