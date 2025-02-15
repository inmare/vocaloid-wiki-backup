from typing import TypedDict


class SongInfo(TypedDict):
    originalUrl: str | None  # 원곡 URL
    # 곡에 참여한 사람, 음합엔
    composer: list[str]
    lyricist: list[str]
    singer: list[str]
    arranger: list[str] | None
    chorus: list[str] | None
    vocaloidEditor: list[str] | None
    illustrator: list[str] | None
    videoProducer: list[str] | None
    engineering: list[str] | None
    mixing: list[str] | None
    mastering: list[str] | None
    pianist: list[str] | None
    guitarist: list[str] | None
    bassist: list[str] | None
    drummer: list[str] | None
    trumpeter: list[str] | None
    trombonist: list[str] | None
    altoSaxophonist: list[str] | None
    playerEtc: list[str] | None


class LyricsInfo(TypedDict):
    lyrics: list[str]  # 가사
    version: str | None


class PageInfo(TypedDict):
    pageUrl: str  # 페이지 URL, 상대 경로
    pageTitle: str  # 번역된 제목, 중복된 제목의 경우 작곡가가 제목에 포함될 수 있음
    originalPageTitle: str | None  # 중복된 제목의 경우 작곡가를 제외한 원래 제목
    originalTitle: str  # 원 제목
    songInfo: list[SongInfo]
    lyricsInfo: list[LyricsInfo]


class SongMetaInfo(TypedDict):
    name: str
    mustSame: bool
    phrase: list[str]


SONG_META_INFO = [
    SongMetaInfo(
        name="composer",
        mustSame=True,
        phrase=["작곡", "작사작곡", "곡과 시"],
    ),
    SongMetaInfo(
        name="lyricist",
        mustSame=True,
        phrase=["작사", "작사 협력", "작사작곡", "곡과 시"],
    ),
    SongMetaInfo(
        name="singer",
        mustSame=False,
        phrase=["노래", "나레이션", "대사", "피처링", "삐뽀삐뽀"],
    ),
    SongMetaInfo(
        name="arranger",
        mustSame=False,
        phrase=["편곡", "재편곡", "브라스 편곡", "피아노 편곡"],
    ),
    SongMetaInfo(
        name="chorus",
        mustSame=False,
        phrase=["코러스", "보컬 서포트"],
    ),
    SongMetaInfo(
        name="vocaloidEditor",
        mustSame=False,
        phrase=["조교", "음과 조교"],
    ),
    SongMetaInfo(
        name="illustrator",
        mustSame=False,
        phrase=["일러스트", "그림", "그림과 영상"],
    ),
    SongMetaInfo(
        name="videoProducer",
        mustSame=False,
        phrase=["영상", "그림과 영상"],
    ),
    SongMetaInfo(
        name="engineering",
        mustSame=False,
        phrase=["엔지니어링", "브라스 녹음 엔지니어", "레코딩"],
    ),
    SongMetaInfo(
        name="mixing",
        mustSame=False,
        phrase=["믹싱", "믹스", "보카로 믹싱 엔지니어"],
    ),
    SongMetaInfo(
        name="mastering",
        mustSame=False,
        phrase=["마스터링"],
    ),
    SongMetaInfo(
        name="pianist",
        mustSame=False,
        phrase=["피아노", "키보드", "신디사이저", "신스", "재즈피아노"],
    ),
    SongMetaInfo(
        name="guitarist",
        mustSame=False,
        phrase=["기타", "기타 솔로"],
    ),
    SongMetaInfo(
        name="bassist",
        mustSame=False,
        phrase=["베이스"],
    ),
    SongMetaInfo(
        name="drummer",
        mustSame=False,
        phrase=["드럼"],
    ),
    SongMetaInfo(
        name="trumpeter",
        mustSame=False,
        phrase=["트럼펫"],
    ),
    SongMetaInfo(
        name="trombonist",
        mustSame=False,
        phrase=["트럼본"],
    ),
    SongMetaInfo(
        name="altoSaxophonist",
        mustSame=False,
        phrase=["알토 색소폰"],
    ),
    SongMetaInfo(
        name="playerEtc",
        mustSame=False,
        phrase=["연주", "원곡", "하이라이트", "밴드", "스크래치", "코러스 제작"],
    ),
]
