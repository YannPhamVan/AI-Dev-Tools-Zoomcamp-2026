"""Database-backed store using SQLAlchemy, configurable via DATABASE_URL."""

import os
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Generator

from sqlalchemy import Column, Integer, String, create_engine, desc, select
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./snake.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class PlayerModel(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    high_score = Column(Integer, default=0, nullable=False)


class TokenModel(Base):
    __tablename__ = "tokens"

    token = Column(String, primary_key=True, index=True)
    username = Column(String, index=True, nullable=False)


@dataclass
class PlayerRecord:
    username: str
    hashed_password: str
    high_score: int


class Store:
    def __init__(self):
        Base.metadata.create_all(bind=engine)
        self._seed()

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        session = SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def _seed(self) -> None:
        """Seed demo players if table is empty."""
        demo = [
            ("cobra_kai", "demo", 87),
            ("viper", "demo", 74),
            ("mamba", "demo", 66),
            ("python42", "demo", 58),
            ("slither", "demo", 51),
            ("anaconda", "demo", 44),
            ("boa", "demo", 37),
            ("adder", "demo", 29),
            ("rattler", "demo", 22),
            ("garter", "demo", 15),
            ("newbie", "demo", 8),
        ]
        with self.get_session() as session:
            count = session.query(PlayerModel).count()
            if count == 0:
                from backend.auth import hash_password

                for uname, pwd, score in demo:
                    session.add(
                        PlayerModel(
                            username=uname,
                            hashed_password=hash_password(pwd),
                            high_score=score,
                        )
                    )

    def username_exists(self, username: str) -> bool:
        with self.get_session() as session:
            stmt = select(PlayerModel).where(PlayerModel.username == username.strip())
            return session.scalars(stmt).first() is not None

    def create_player(self, username: str, hashed_password: str) -> PlayerRecord:
        uname = username.strip()
        with self.get_session() as session:
            player = PlayerModel(
                username=uname,
                hashed_password=hashed_password,
                high_score=0,
            )
            session.add(player)
            session.flush()
            return PlayerRecord(
                username=player.username,
                hashed_password=player.hashed_password,
                high_score=player.high_score,
            )

    def get_player(self, username: str) -> PlayerRecord | None:
        with self.get_session() as session:
            stmt = select(PlayerModel).where(PlayerModel.username == username.strip())
            player = session.scalars(stmt).first()
            if not player:
                return None
            return PlayerRecord(
                username=player.username,
                hashed_password=player.hashed_password,
                high_score=player.high_score,
            )

    def update_high_score(self, username: str, score: int) -> tuple[PlayerRecord, bool]:
        with self.get_session() as session:
            stmt = select(PlayerModel).where(PlayerModel.username == username.strip())
            player = session.scalars(stmt).first()
            if not player:
                raise KeyError(f"Player {username} does not exist")
            is_new = score > player.high_score
            if is_new:
                player.high_score = score
                session.flush()
            return (
                PlayerRecord(
                    username=player.username,
                    hashed_password=player.hashed_password,
                    high_score=player.high_score,
                ),
                is_new,
            )

    def leaderboard(self, limit: int = 10) -> list[PlayerRecord]:
        with self.get_session() as session:
            stmt = (
                select(PlayerModel)
                .order_by(desc(PlayerModel.high_score), PlayerModel.username)
                .limit(limit)
            )
            players = session.scalars(stmt).all()
            return [
                PlayerRecord(
                    username=p.username,
                    hashed_password=p.hashed_password,
                    high_score=p.high_score,
                )
                for p in players
            ]

    def save_token(self, token: str, username: str) -> None:
        with self.get_session() as session:
            session.merge(TokenModel(token=token, username=username))

    def get_token_username(self, token: str) -> str | None:
        with self.get_session() as session:
            stmt = select(TokenModel).where(TokenModel.token == token)
            record = session.scalars(stmt).first()
            return record.username if record else None

    def revoke_token(self, token: str) -> None:
        with self.get_session() as session:
            stmt = select(TokenModel).where(TokenModel.token == token)
            record = session.scalars(stmt).first()
            if record:
                session.delete(record)


store = Store()
