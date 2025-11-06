# app/api/v1/endpoints/dashboard.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract
from typing import List
from datetime import datetime

from api.db.session import get_db
from api.models.user import User
from api.models.expense import Expense, ExpenseType
from api.models.category import Category
from api.models.income import Income, VariableIncome, FixedIncome
from api.schemas.analytics import DashboardStats
from api.schemas.expense import ExpenseResponse
from api.api.deps import get_current_user

router = APIRouter()


@router.get("/stats/", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    now = datetime.now()

    # Receitas fixas mensais (Income.fixed_amount)
    result = await db.execute(
        select(Income).where(Income.user_id == current_user.id)
    )
    income_config = result.scalar_one_or_none()
    fixed_monthly_income = income_config.fixed_amount if income_config else 0

    # Receitas variáveis ativas (VariableIncome)
    result = await db.execute(
        select(func.sum(VariableIncome.amount))
        .join(Income, VariableIncome.income_id == Income.id)
        .where(
            Income.user_id == current_user.id,
            VariableIncome.is_active == True
        )
    )
    variable_income = result.scalar() or 0

    # Receitas fixas adicionais (FixedIncome)
    result = await db.execute(
        select(func.sum(FixedIncome.amount)).where(
            FixedIncome.user_id == current_user.id,
            FixedIncome.is_active == True
        )
    )
    fixed_incomes = result.scalar() or 0

    # Total das receitas (expenses do tipo RECEITA)
    result = await db.execute(
        select(func.sum(Expense.amount)).where(
            Expense.user_id == current_user.id,
            Expense.type == ExpenseType.RECEITA
        )
    )
    total_expense_income = result.scalar() or 0

    # Total das receitas = receita fixa mensal + variáveis ativas + fixas adicionais + receitas via expenses
    total_income = fixed_monthly_income + variable_income + fixed_incomes + total_expense_income

    # Total das despesas
    result = await db.execute(
        select(func.sum(Expense.amount)).where(
            Expense.user_id == current_user.id,
            Expense.type == ExpenseType.DESPESA
        )
    )
    total_expenses = result.scalar() or 0

    # Receitas do mês (expenses do tipo RECEITA no mês atual)
    result = await db.execute(
        select(func.sum(Expense.amount)).where(
            Expense.user_id == current_user.id,
            Expense.type == ExpenseType.RECEITA,
            extract('month', Expense.date) == now.month,
            extract('year', Expense.date) == now.year
        )
    )
    monthly_expense_income = result.scalar() or 0

    # Receitas mensais = receita fixa mensal + variáveis ativas + fixas adicionais + receitas via expenses do mês
    monthly_income = fixed_monthly_income + variable_income + fixed_incomes + monthly_expense_income

    # Despesas do mês
    result = await db.execute(
        select(func.sum(Expense.amount)).where(
            Expense.user_id == current_user.id,
            Expense.type == ExpenseType.DESPESA,
            extract('month', Expense.date) == now.month,
            extract('year', Expense.date) == now.year
        )
    )
    monthly_expenses = result.scalar() or 0

    # Categorias ativas
    result = await db.execute(
        select(func.count(Category.id)).where(
            Category.user_id == current_user.id
        )
    )
    active_categories = result.scalar() or 0

    return DashboardStats(
        total_balance=total_income - total_expenses,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        active_categories=active_categories
    )


@router.get("/recent-transactions/", response_model=List[ExpenseResponse])
async def get_recent_transactions(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    now = datetime.now()
    result = await db.execute(
        select(Expense)
        .where(
            Expense.user_id == current_user.id,
            extract('month', Expense.date) == now.month,
            extract('year', Expense.date) == now.year
        )
        .order_by(Expense.date.desc(), Expense.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/all-transactions/", response_model=List[ExpenseResponse])
async def get_all_transactions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Expense)
        .where(Expense.user_id == current_user.id)
        .order_by(Expense.date.desc(), Expense.created_at.desc())
    )
    return result.scalars().all()

