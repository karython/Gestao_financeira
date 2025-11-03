# app/schemas/reports.py
from pydantic import BaseModel, EmailStr
from typing import Optional


class ReportRequest(BaseModel):
    type: str
    category_id: Optional[int] = None
    month: int
    year: int


class ReportEmailRequest(ReportRequest):
    email: EmailStr
