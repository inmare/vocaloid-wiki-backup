from sqlmodel import SQLModel, Field, create_engine, Session, Relationship, select, col
import json
import os


class GroupTitle(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    url: str

    songs: list["Song"] = Relationship(back_populates="group_title")


class Song(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    page_url: str
    original_title: str
    translated_title: str | None = Field(default=None)
    # 제목이 중복되는 곡의 경우 사용되는 제목
    # alt_title: str | None = Field(default=None)
    composer: str
    lyricist: str | None = Field(default=None)
    arranger: str | None = Field(default=None)
    illustrator: str | None = Field(default=None)
    chorus: str | None = Field(default=None)
    singer: str
    lyrics: str

    group_title_id: int | None = Field(default=None, foreign_key="grouptitle.id")
    group_title: GroupTitle = Relationship(back_populates="songs")


sqlite_file_name = "temp/vocaloid_lyrics_wiki.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)


def create_db_and_tables():
    if os.path.exists(sqlite_file_name):
        os.remove(sqlite_file_name)
    SQLModel.metadata.create_all(engine)


def create_song(song: Song):
    with Session(engine) as session:
        session.add(song)
        session.commit()


def arr_to_str(arr: list[str]) -> str:
    return json.dumps(arr, ensure_ascii=False)


def main():
    create_db_and_tables()
    json_files = os.listdir("./json/h1")

    with Session(engine) as session:
        title_h1 = GroupTitle(title="ㄱ", url="allsongs-h1")
        try:
            for json_file in json_files:
                json_info = json.load(
                    open(f"./json/h1/{json_file}", "r", encoding="utf-8")
                )
                # 같은 제목의 곡이 2개 이상인 경우 제목/작곡가의 링크들로 이루어져 있는 페이지 존재
                # 해당 페이지에 대한 예외 추후에 처리
                if not json_info["lyrics"]:
                    print("Page Error: ", json_info["page"])
                    continue

                # json파일에 singer키가 없으면 if문 출력
                if "singer" not in json_info:
                    print("Singer Error: ", json_info["page"])
                    continue

                # 작사 작곡을 한 사람이 맡고 편곡을 따로 분리한 경우에 대한 예외를 임시로 처리하기 위한 방법
                # 일부 작사, 작곡, 편곡을 한 사람의 경우 링크가 없는 경우가 있기에
                # 크롤링시 해당 예외에 대한 처리도 필요함
                # 표를 크롤링하면서 기존의 템플릿에서 벗어나는 경우를 따로 저장함
                composer = json_info["composer"]
                lyricist = (
                    json_info["lyricist"]
                    if "lyricist" in json_info
                    else json_info["composer"]
                )
                singer = (
                    json_info["singer"]
                    if "singer" in json_info
                    else json_info["lyricist"]
                )
                song = Song(
                    page_url=json_info["url"],
                    original_title=json_info["title"],
                    translated_title=json_info["page"],
                    composer=arr_to_str([composer]),
                    lyricist=arr_to_str([lyricist]),
                    singer=arr_to_str([singer]),
                    lyrics=arr_to_str(json_info["lyrics"]),
                    group_title=title_h1,
                )
                create_song(song)
                session.add(song)
                session.commit()
        except Exception as e:
            print(json_info)
            print(e)


def find_songs():
    with Session(engine) as session:
        # statement = select(Song).where(Song.translated_title == "가")
        title_statement = select(GroupTitle).where(GroupTitle.title == "ㄱ")
        title_results = session.exec(title_statement).one()
        # 임시로 넣은 분류
        # ㄱ으로 시작하는 곡들 중에서 가로 시작하는 곡들만 출력
        song_statement = (
            select(Song)
            .where(Song.group_title_id == title_results.id)
            .where(Song.translated_title.startswith("가"))
        )
        results = session.exec(song_statement)
        for song in results:
            print(song.translated_title)


if __name__ == "__main__":
    # main()
    find_songs()
