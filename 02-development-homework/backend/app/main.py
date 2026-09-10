from fastapi import FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware

from .schemas import (
    BalanceResponse,
    CreateExpenseRequest,
    CreateMemberRequest,
    CreateTripRequest,
    ExpenseResponse,
    MemberResponse,
    SettlementResponse,
    TripResponse,
)
from .models import Trip
from .store import store

app = FastAPI(title="ShareTrip API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_trip_or_404(trip_id: str) -> Trip:
    trip = store.get_trip(trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


def expense_response(expense) -> ExpenseResponse:
    return ExpenseResponse.model_validate(expense, from_attributes=True)


def trip_response(trip: Trip) -> TripResponse:
    return TripResponse(
        id=trip.id,
        name=trip.name,
        members=[MemberResponse.model_validate(member, from_attributes=True) for member in trip.members],
        expenses=[expense_response(expense) for expense in trip.expenses],
    )


def balances_for(trip: Trip) -> dict[str, float]:
    share = sum(expense.amount for expense in trip.expenses) / len(trip.members) if trip.members else 0
    return {
        member.id: round(
            sum(expense.amount for expense in trip.expenses if expense.paid_by == member.id) - share,
            2,
        )
        for member in trip.members
    }


def settlements_for(trip: Trip) -> list[SettlementResponse]:
    balances = balances_for(trip)
    debtors = [[member_id, amount] for member_id, amount in balances.items() if amount < -0.01]
    creditors = [[member_id, amount] for member_id, amount in balances.items() if amount > 0.01]
    debtors.sort(key=lambda item: item[1])
    creditors.sort(key=lambda item: item[1], reverse=True)

    settlements = []
    debtor_index = creditor_index = 0
    while debtor_index < len(debtors) and creditor_index < len(creditors):
        debtor_id, debtor_balance = debtors[debtor_index]
        creditor_id, creditor_balance = creditors[creditor_index]
        amount = round(min(-debtor_balance, creditor_balance), 2)
        settlements.append(
            SettlementResponse(
                from_member_id=debtor_id,
                to_member_id=creditor_id,
                amount=amount,
            )
        )
        debtors[debtor_index][1] = round(debtor_balance + amount, 2)
        creditors[creditor_index][1] = round(creditor_balance - amount, 2)
        if abs(debtors[debtor_index][1]) < 0.01:
            debtor_index += 1
        if abs(creditors[creditor_index][1]) < 0.01:
            creditor_index += 1
    return settlements


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/trips", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def create_trip(payload: CreateTripRequest):
    return trip_response(store.create_trip(payload.name))


@app.get("/trips/{trip_id}", response_model=TripResponse)
def get_trip(trip_id: str):
    return trip_response(get_trip_or_404(trip_id))


@app.post("/trips/{trip_id}/members", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(trip_id: str, payload: CreateMemberRequest):
    trip = get_trip_or_404(trip_id)
    if any(member.name.casefold() == payload.name.casefold() for member in trip.members):
        raise HTTPException(status_code=409, detail="Member already exists")
    return store.add_member(trip.id, payload.name)


@app.post("/trips/{trip_id}/expenses", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(trip_id: str, payload: CreateExpenseRequest):
    trip = get_trip_or_404(trip_id)
    if not any(member.id == payload.paid_by for member in trip.members):
        raise HTTPException(status_code=404, detail="Payer not found")
    return store.add_expense(trip.id, payload.description, payload.amount, payload.paid_by)


@app.get("/trips/{trip_id}/expenses", response_model=list[ExpenseResponse])
def list_expenses(trip_id: str):
    trip = get_trip_or_404(trip_id)
    return sorted(trip.expenses, key=lambda expense: expense.created_at, reverse=True)


@app.delete("/trips/{trip_id}/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_expense(trip_id: str, expense_id: str):
    trip = get_trip_or_404(trip_id)
    if not store.delete_expense(expense_id):
        raise HTTPException(status_code=404, detail="Expense not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/trips/{trip_id}/balances", response_model=list[BalanceResponse])
def list_balances(trip_id: str):
    trip = get_trip_or_404(trip_id)
    return [BalanceResponse(member_id=member_id, balance=balance) for member_id, balance in balances_for(trip).items()]


@app.get("/trips/{trip_id}/settlements", response_model=list[SettlementResponse])
def list_settlements(trip_id: str):
    return settlements_for(get_trip_or_404(trip_id))
