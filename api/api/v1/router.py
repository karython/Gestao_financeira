# app/api/v1/router.py
from fastapi import APIRouter
from api.api.v1.endpoints import (
    auth, categorias as categories, expenses, fixed_expenses,
    income, reports, analytics, dashboard
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["expenses"])
api_router.include_router(fixed_expenses.router, prefix="/fixed-expenses", tags=["fixed-expenses"])
api_router.include_router(income.router, prefix="/income", tags=["income"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])