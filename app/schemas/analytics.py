# app/schemas/analytics.py
from pydantic import BaseModel
from decimal import Decimal
from typing import List, Dict


class SummaryResponse(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    balance: Decimal
    month: int
    year: int


class ChartDataResponse(BaseModel):
    labels: List[str]
    data: List[Decimal]


class DashboardStats(BaseModel):
    total_balance: Decimal
    monthly_income: Decimal
    monthly_expenses: Decimal
    active_categories: int

