# app/schemas/expense.py
from pydantic import BaseModel, validator
from datetime import date, datetime
from decimal import Decimal
from typing import Union
from api.models.expense import ExpenseType


class ExpenseBase(BaseModel):
    description: str
    amount: Decimal
    category_id: int
    date: date
    # accept either the enum or a string (case-insensitive) from clients
    type: Union[ExpenseType, str]

    @validator("type", pre=True)
    def validate_type(cls, v):
        # allow passing the enum instance through
        if isinstance(v, ExpenseType):
            return v
        if isinstance(v, str):
            lowered = v.lower()
            for et in ExpenseType:
                if lowered == et.value:
                    return et
        raise ValueError("type must be one of: 'despesa' or 'receita'")


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
