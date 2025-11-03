# app/schemas/fixed_expense.py
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class FixedExpenseBase(BaseModel):
    description: str
    amount: Decimal
    category_id: int
    day_of_month: int


class FixedExpenseCreate(FixedExpenseBase):
    pass


class FixedExpenseUpdate(FixedExpenseBase):
    pass


class FixedExpenseResponse(FixedExpenseBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
