# app/schemas/reports.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date


class ReportRequest(BaseModel):
    type: str
    category_id: Optional[int] = None
    month: Optional[int] = None
    year: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ReportEmailRequest(ReportRequest):
    email: EmailStr
