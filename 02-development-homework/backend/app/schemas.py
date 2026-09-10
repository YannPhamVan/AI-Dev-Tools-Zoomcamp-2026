from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class CreateTripRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("name must not be blank")
        return value


class CreateMemberRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("name must not be blank")
        return value


class CreateExpenseRequest(BaseModel):
    description: str = Field(min_length=1, max_length=160)
    amount: float = Field(gt=0)
    paid_by: str = Field(min_length=1)

    @field_validator("description")
    @classmethod
    def description_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("description must not be blank")
        return value


class MemberResponse(BaseModel):
    id: str
    name: str


class ExpenseResponse(BaseModel):
    id: str
    description: str
    amount: float
    paid_by: str
    created_at: datetime


class TripResponse(BaseModel):
    id: str
    name: str
    members: list[MemberResponse]
    expenses: list[ExpenseResponse]


class BalanceResponse(BaseModel):
    member_id: str
    balance: float


class SettlementResponse(BaseModel):
    from_member_id: str
    to_member_id: str
    amount: float
