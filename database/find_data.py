from sqlmodel import create_engine, Session, select
from utils.parse_text import TextType
from database.db_types import TitleType


sqlite_file_name = "database/vocaloid-lyrics-wiki.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)


def find_text_type_id(text_type: TextType) -> int:
    """
    문자의 시작 글자가 어떤 타입인지 반환
    """
    with Session(engine) as session:
        statement = select(TitleType).where(TitleType.titleType == text_type.name)
        result = session.exec(statement)
        text_type_id = result.one().id
    return text_type_id
