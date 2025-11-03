# app/schemas/income.py
from pydantic import BaseModel, validator
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Optional


class IncomeBase(BaseModel):
    fixed_amount: Decimal = Decimal("0")
    bonus_amount: Decimal = Decimal("0")


class IncomeUpdate(IncomeBase):
    pass


class IncomeResponse(IncomeBase):
    id: int
    user_id: int
    created_at: datetime
    class Config:
        orm_mode = True


class VariableIncomeBase(BaseModel):
    description: str
    amount: Decimal
    valid_until: Optional[datetime] = None

    @validator("amount", pre=True)
    def coerce_amount(cls, v):
        # accept str, float, int and convert to Decimal
        if isinstance(v, Decimal):
            return v
        try:
            return Decimal(str(v))
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError("amount must be a decimal number")

    @validator("valid_until", pre=True)
    def parse_valid_until(cls, v):
        # Accept date-only strings like 'YYYY-MM-DD' and convert to datetime at midnight
        if v is None:
            return None
        if isinstance(v, datetime):
            return v
        if isinstance(v, date):
            return datetime(v.year, v.month, v.day)
        if isinstance(v, str):
            try:
                # date-only format
                if len(v) == 10 and v.count("-") == 2:
                    d = date.fromisoformat(v)
                    return datetime(d.year, d.month, d.day)
                # try full datetime ISO format
                return datetime.fromisoformat(v)
            except Exception:
                raise ValueError("valid_until must be a valid ISO date or datetime string")


class VariableIncomeCreate(VariableIncomeBase):
    pass


class VariableIncomeUpdate(VariableIncomeBase):
    pass


class VariableIncomeResponse(VariableIncomeBase):
    id: int
    income_id: int
    is_active: bool
    created_at: datetime
    class Config:
        orm_mode = True


class FixedIncomeBase(BaseModel):
    description: str
    amount: Decimal
    is_active: bool = True

    @validator("amount", pre=True)
    def coerce_amount(cls, v):
        # accept str, float, int and convert to Decimal
        if isinstance(v, Decimal):
            return v
        try:
            return Decimal(str(v))
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError("amount must be a decimal number")


class FixedIncomeCreate(FixedIncomeBase):
    pass


class FixedIncomeUpdate(FixedIncomeBase):
    pass


class FixedIncomeResponse(FixedIncomeBase):
    id: int
    user_id: int
    created_at: datetime
    class Config:
        orm_mode = True

