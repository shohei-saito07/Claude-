from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

DEFAULT_DATABASE_URL = "sqlite:///./url_shortener.db"


def make_engine(database_url: str = DEFAULT_DATABASE_URL) -> Engine:
    kwargs: dict = {}
    if database_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    if database_url == "sqlite:///:memory:":
        # A single shared connection so the in-memory DB persists across requests.
        kwargs["poolclass"] = StaticPool
    return create_engine(database_url, **kwargs)


def init_db(engine: Engine) -> None:
    SQLModel.metadata.create_all(engine)
