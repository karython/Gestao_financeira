# app/api/v1/endpoints/fixed_expenses.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, extract
from typing import List
from datetime import date

from app.db.session import get_db
from app.models.user import User
from app.models.fixed_expense import FixedExpense
from app.models.expense import Expense, ExpenseType
from app.schemas.fixed_expense import FixedExpenseCreate, FixedExpenseUpdate, FixedExpenseResponse
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[FixedExpenseResponse])
async def list_fixed_expenses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(FixedExpense).where(FixedExpense.user_id == current_user.id)
    )
    return result.scalars().all()


@router.post("/", response_model=FixedExpenseResponse, status_code=201)
async def create_fixed_expense(
    fixed_expense_in: FixedExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    fixed_expense = FixedExpense(**fixed_expense_in.dict(), user_id=current_user.id)
    db.add(fixed_expense)
    await db.commit()
    await db.refresh(fixed_expense)
    return fixed_expense


@router.put("/{fixed_expense_id}/", response_model=FixedExpenseResponse)
async def update_fixed_expense(
    fixed_expense_id: int,
    fixed_expense_update: FixedExpenseUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(FixedExpense).where(
            FixedExpense.id == fixed_expense_id,
            FixedExpense.user_id == current_user.id
        )
    )
    fixed_expense = result.scalar_one_or_none()
    if not fixed_expense:
        raise HTTPException(status_code=404, detail="Despesa fixa não encontrada")
    
    for key, value in fixed_expense_update.dict().items():
        setattr(fixed_expense, key, value)
    
    await db.commit()
    await db.refresh(fixed_expense)
    return fixed_expense


@router.delete("/{fixed_expense_id}/")
async def delete_fixed_expense(
    fixed_expense_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(FixedExpense).where(
            FixedExpense.id == fixed_expense_id,
            FixedExpense.user_id == current_user.id
        )
    )
    fixed_expense = result.scalar_one_or_none()
    if not fixed_expense:
        raise HTTPException(status_code=404, detail="Despesa fixa não encontrada")
    
    await db.delete(fixed_expense)
    await db.commit()
    return {"message": "Despesa fixa removida com sucesso"}


@router.post("/process-monthly/")
async def process_monthly_fixed_expenses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    today = date.today()
    
    result = await db.execute(
        select(FixedExpense).where(
            FixedExpense.user_id == current_user.id,
            FixedExpense.is_active == True
        )
    )
    fixed_expenses = result.scalars().all()
    
    created_count = 0
    for fixed in fixed_expenses:
        expense_date = date(today.year, today.month, min(fixed.day_of_month, 28))
        
        existing = await db.execute(
            select(Expense).where(
                Expense.user_id == current_user.id,
                Expense.description == fixed.description,
                extract('month', Expense.date) == today.month,
                extract('year', Expense.date) == today.year
            )
        )
        
        if not existing.scalar_one_or_none():
            expense = Expense(
                user_id=current_user.id,
                category_id=fixed.category_id,
                description=fixed.description,
                amount=fixed.amount,
                date=expense_date,
                type=ExpenseType.DESPESA
            )
            db.add(expense)
            created_count += 1
    
    await db.commit()
    return {"message": f"{created_count} despesas fixas processadas para o mês atual"}

