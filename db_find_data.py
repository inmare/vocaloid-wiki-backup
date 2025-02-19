from sqlmodel import SQLModel, Session, select, create_engine
from database.db_types import Page, Song, Lyrics, TitleType
from utils.parse_text import TextType, KOREAN_TABLE, get_text_start_type

sqlite_file_name = "database/vocaloid-lyrics-wiki.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)


def find_page() -> Page:
    h1 = TextType.h1
    latin = TextType.latin
    with Session(engine) as session:
        h1_statement = select(TitleType).where(TitleType.titleType == TextType.h1.name)
        h1 = session.exec(h1_statement).first()
        h1_id = h1.id

        statement = (
            select(Page)
            .where(Page.titleTypeId == h1_id)
            .order_by(Page.pageTitle)
            # .limit(10)
        )
        results = session.exec(statement)
        pages = results.all()

        print(len(pages))

        # for page in pages:
        #     print(page.pageTitle, "-", page.songs[0].composer)


if __name__ == "__main__":
    find_page()
