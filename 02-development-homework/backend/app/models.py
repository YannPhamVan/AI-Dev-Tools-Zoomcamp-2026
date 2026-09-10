from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex}"


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[str] = mapped_column(String(80), primary_key=True, default=lambda: new_id("trip"))
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    members: Mapped[list["Member"]] = relationship(
        back_populates="trip", cascade="all, delete-orphan", order_by="Member.created_at"
    )
    expenses: Mapped[list["Expense"]] = relationship(
        back_populates="trip", cascade="all, delete-orphan", order_by="Expense.created_at"
    )


class Member(Base):
    __tablename__ = "members"

    id: Mapped[str] = mapped_column(String(80), primary_key=True, default=lambda: new_id("member"))
    trip_id: Mapped[str] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    trip: Mapped[Trip] = relationship(back_populates="members")


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[str] = mapped_column(String(80), primary_key=True, default=lambda: new_id("expense"))
    trip_id: Mapped[str] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(160), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    paid_by: Mapped[str] = mapped_column(ForeignKey("members.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    trip: Mapped[Trip] = relationship(back_populates="expenses")
