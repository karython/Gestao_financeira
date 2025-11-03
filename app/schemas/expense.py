# app/schemas/expense.py
from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
from app.models.expense import ExpenseType


class ExpenseBase(BaseModel):
    description: str
    amount: Decimal
    category_id: int
    date: date
    type: ExpenseType


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(ExpenseBase):
    pass


class ExpenseResponse(ExpenseBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
