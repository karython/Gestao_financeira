# app/api/v1/endpoints/analytics.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, extract, func
from typing import Optional
from decimal import Decimal
from datetime import datetime

from api.db.session import get_db
from api.models.user import User
from api.models.expense import Expense, ExpenseType
from api.models.category import Category
from api.schemas.analytics import SummaryResponse, ChartDataResponse, DashboardStats
from api.api.deps import get_current_user

router = APIRouter()


@router.get("/summary/", response_model=SummaryResponse)
async def get_summary(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Expense).where(
            Expense.user_id == current_user.id,
            extract('month', Expense.date) == month,
            extract('year', Expense.date) == year
        )
    )
    expenses = result.scalars().all()
    
    total_income = sum(e.amount for e in expenses if e.type == ExpenseType.RECEITA)
    total_expenses = sum(e.amount for e in expenses if e.type == ExpenseType.DESPESA)
    
    return SummaryResponse(
        total_income=total_income,
        total_expenses=total_expenses,
        balance=total_income - total_expenses,
        month=month,
        year=year
    )


@router.get("/chart-data/", response_model=ChartDataResponse)
async def get_chart_data(
    filter: str = Query(..., description="entradas, saidas, categorias"),
    period: str = Query("mensal", description="mensal, anual"),
    month: Optional[int] = Query(None, ge=1, le=12),
    year: int = Query(..., ge=2000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if filter == "categorias":
        query = select(
            Category.name,
            func.sum(Expense.amount).label('total')
        ).join(
            Expense, Expense.category_id == Category.id
        ).where(
            Expense.user_id == current_user.id,
            extract('year', Expense.date) == year
        )
        
        if month:
            query = query.where(extract('month', Expense.date) == month)
        
        query = query.group_by(Category.name)
        
        result = await db.execute(query)
        data = result.all()
        
        return ChartDataResponse(
            labels=[row[0] for row in data],
            data=[row[1] for row in data]
        )
    
    elif filter == "entradas":
        query = select(Expense).where(
            Expense.user_id == current_user.id,
            Expense.type == ExpenseType.RECEITA,
            extract('year', Expense.date) == year
        )
        
        if period == "mensal" and month:
            query = query.where(extract('month', Expense.date) == month)
        
        result = await db.execute(query)
        expenses = result.scalars().all()
        
        if period == "mensal":
            labels = [str(i) for i in range(1, 32)]
            data = [Decimal(0)] * 31
            for exp in expenses:
                data[exp.date.day - 1] += exp.amount
        else:
            labels = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
            data = [Decimal(0)] * 12
            for exp in expenses:
                data[exp.date.month - 1] += exp.amount
        
        return ChartDataResponse(labels=labels, data=data)
    
    else:  # saidas
        query = select(Expense).where(
            Expense.user_id == current_user.id,
            Expense.type == ExpenseType.DESPESA,
            extract('year', Expense.date) == year
        )
        
        if period == "mensal" and month:
            query = query.where(extract('month', Expense.date) == month)
        
        result = await db.execute(query)
        expenses = result.scalars().all()
        
        if period == "mensal":
            labels = [str(i) for i in range(1, 32)]
            data = [Decimal(0)] * 31
            for exp in expenses:
                data[exp.date.day - 1] += exp.amount
        else:
            labels = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
            data = [Decimal(0)] * 12
            for exp in expenses:
                data[exp.date.month - 1] += exp.amount
        
        return ChartDataResponse(labels=labels, data=data)

