# app/api/v1/endpoints/expenses.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, extract
from typing import List, Optional
from datetime import datetime

from api.db.session import get_db
from api.models.user import User
from api.models.expense import Expense, ExpenseType
from api.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from api.api.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ExpenseResponse])
async def list_expenses(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000),
    start_date: Optional[str] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Data final (YYYY-MM-DD)"),
    type: Optional[ExpenseType] = None,
    category_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Expense).where(Expense.user_id == current_user.id)

    if month:
        query = query.where(extract('month', Expense.date) == month)
    if year:
        query = query.where(extract('year', Expense.date) == year)
    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        query = query.where(Expense.date >= start)
    if end_date:
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        query = query.where(Expense.date <= end)
    if type:
        query = query.where(Expense.type == type)
    if category_id:
        query = query.where(Expense.category_id == category_id)

    result = await db.execute(query.order_by(Expense.date.desc()))
    return result.scalars().all()


@router.post("/", response_model=ExpenseResponse, status_code=201)
async def create_expense(
    expense_in: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    expense = Expense(**expense_in.dict(), user_id=current_user.id)
    db.add(expense)
    await db.commit()
    await db.refresh(expense)
    return expense


@router.put("/{expense_id}/", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    expense_update: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Expense).where(
            Expense.id == expense_id,
            Expense.user_id == current_user.id
        )
    )
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado")
    
    for key, value in expense_update.dict().items():
        setattr(expense, key, value)
    
    await db.commit()
    await db.refresh(expense)
    return expense


@router.delete("/{expense_id}/")
async def delete_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Expense).where(
            Expense.id == expense_id,
            Expense.user_id == current_user.id
        )
    )
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado")
    
    await db.delete(expense)
    await db.commit()
    return {"message": "Lançamento removido com sucesso"}
