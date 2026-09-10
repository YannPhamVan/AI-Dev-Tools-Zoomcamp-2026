"""Database-backed store using SQLAlchemy, configurable via DATABASE_URL."""

import os
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Generator

from sqlalchemy import Column, Integer, String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./snake.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):