from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .database import Base, build_engine, session_factory
from .models import Expense, Member, Trip


class DatabaseStore:
    def __init__(self, database_url: str | None = None):
        self.configure(database_url)

    def configure(self, database_url: str | None = None):
        if hasattr(self, "engine"):
            self.engine.dispose()
        self.engine = build_engine(database_url)
        self.session_local = session_factory(self.engine)
        Base.metadata.create_all(self.engine)

    def reset(self):
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

    def create_trip(self, name: str) -> Trip:
        with self.session_local() as session:
            trip = Trip(name=name)
            session.add(trip)
            session.commit()
            trip_id = trip.id
        return self.get_trip(trip_id)

    def get_trip(self, trip_id: str) -> Trip | None:
        with self.session_local() as session:
            return session.scalar(
                select(Trip)
                .options(selectinload(Trip.members), selectinload(Trip.expenses))
                .where(Trip.id == trip_id)
            )

    def add_member(self, trip_id: str, name: str) -> Member:
        with self.session_local() as session:
            member = Member(trip_id=trip_id, name=name)
            session.add(member)
            session.commit()
            return member

    def add_expense(self, trip_id: str, description: str, amount: float, paid_by: str) -> Expense:
        with self.session_local() as session:
            expense = Expense(trip_id=trip_id, description=description, amount=round(amount, 2), paid_by=paid_by)
            session.add(expense)
            session.commit()
            return expense

    def delete_expense(self, expense_id: str) -> bool:
        with self.session_local() as session:
            expense = session.get(Expense, expense_id)
            if expense is None:
                return False
            session.delete(expense)
            session.commit()
            return True


store = DatabaseStore()
