from typing import TypedDict


class SongInfo(TypedDict):
    originalUrl: str | None  # 원곡 URL
    # 곡에 참여한 사람, 음합엔
    composer: list[str] | None
    lyricist: list[str]
    singer: list[str]
    originalSong: list[str] | None
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


class SongTerm(TypedDict):
    name: str
    mustSame: bool
    term: list[str]


# 위키에서 서로 다른 용어들을 정리한 것
term_dictionary = [
    SongTerm(
        name="작곡",
        mustSame=True,
        term=["작곡", "작사작곡", "곡과 시"],
    ),
    SongTerm(
        name="작사",
        mustSame=True,
        term=["작사", "작사 협력", "작사작곡", "곡과 시"],
    ),
    SongTerm(
        name="노래",
        mustSame=False,
        term=["노래", "나레이션", "대사", "피처링", "삐뽀삐뽀"],
    ),
    SongTerm(
        name="원곡",
        mustSame=False,
        term=["원곡"],
    ),
    SongTerm(
        name="편곡",
        mustSame=False,
        term=["편곡", "재편곡", "브라스 편곡", "피아노 편곡"],
    ),
    SongTerm(
        name="코러스",
        mustSame=False,
        term=["코러스", "보컬 서포트"],
    ),
    SongTerm(
        name="조교",
        mustSame=False,
        term=["조교", "음과 조교"],
    ),
    SongTerm(
        name="일러스트",
        mustSame=False,
        term=["일러스트", "그림", "그림과 영상"],
    ),
    SongTerm(
        name="영상",
        mustSame=False,
        term=["영상", "그림과 영상"],
    ),
    SongTerm(
        name="엔지니어링",
        mustSame=False,
        term=["엔지니어링", "브라스 녹음 엔지니어", "레코딩"],
    ),
    SongTerm(
        name="믹싱",
        mustSame=False,
        term=["믹싱", "믹스", "보카로 믹싱 엔지니어"],
    ),
    SongTerm(
        name="마스터링",
        mustSame=False,
        term=["마스터링"],
    ),
    SongTerm(
        name="피아노",
        mustSame=False,
        term=["피아노", "키보드", "재즈피아노"],
    ),
    SongTerm(
        name="신디사이저저",
        mustSame=False,
        term=["신디사이저", "신스"],
    ),
    SongTerm(
        name="기타",
        mustSame=False,
        term=["기타", "기타 솔로"],
    ),
    SongTerm(
        name="베이스",
        mustSame=False,
        term=["베이스"],
    ),
    SongTerm(
        name="드럼",
        mustSame=False,
        term=["드럼"],
    ),
    SongTerm(
        name="트럼펫",
        mustSame=False,
        term=["트럼펫"],
    ),
    SongTerm(
        name="트럼본",
        mustSame=False,
        term=["트럼본"],
    ),
    SongTerm(
        name="알토 색소폰",
        mustSame=False,
        term=["알토 색소폰"],
    ),
    SongTerm(
        name="연주",
        mustSame=False,
        term=["연주"],
    ),
    SongTerm(
        name="하이라이트",
        mustSame=False,
        term=["하이라이트"],
    ),
    SongTerm(
        name="밴드",
        mustSame=False,
        term=["밴드"],
    ),
    SongTerm(
        name="스크래치",
        mustSame=False,
        term=["스크래치"],
    ),
    # 추후에 확인하고 수정하기
    # http://vocaro.wikidot.com/dear-me
    SongTerm(
        name="코러스 제작",
        mustSame=False,
        term=["코러스 제작"],
    ),
]
