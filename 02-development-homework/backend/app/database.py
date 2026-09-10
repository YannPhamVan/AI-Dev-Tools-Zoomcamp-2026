import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


def build_engine(database_url: str | None = None):
    url = database_url or os.getenv("DATABASE_URL", "sqlite+pysqlite:///./sharetrip.db")
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    pool_options = {"poolclass": StaticPool} if url.endswith(":memory:") else {}
    return create_engine(url, connect_args=connect_args, pool_pre_ping=True, **pool_options)


def session_factory(engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session(session_local: sessionmaker[Session]) -> Generator[Session, None, None]:
    session = session_local()
    try:
        yield session
    finally:
        session.close()
