# app/api/v1/endpoints/income.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from api.db.session import get_db
from api.models.user import User
from api.models.income import Income, VariableIncome, FixedIncome
from api.schemas.income import (
    IncomeResponse, IncomeUpdate,
    VariableIncomeCreate, VariableIncomeUpdate, VariableIncomeResponse,
    FixedIncomeCreate, FixedIncomeUpdate, FixedIncomeResponse
)
from api.api.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=IncomeResponse)
async def get_income(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Income).where(Income.user_id == current_user.id)
    )
    income = result.scalar_one_or_none()
    
    if not income:
        income = Income(user_id=current_user.id)
        db.add(income)
        await db.commit()
        await db.refresh(income)
    
    return income


@router.put("/", response_model=IncomeResponse)
async def update_income(
    income_update: IncomeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Income).where(Income.user_id == current_user.id)
    )
    income = result.scalar_one_or_none()
    
    if not income:
        income = Income(user_id=current_user.id)
        db.add(income)
    
    income.fixed_amount = income_update.fixed_amount
    income.bonus_amount = income_update.bonus_amount
    
    await db.commit()
    await db.refresh(income)
    return income


@router.get("/variable/", response_model=List[VariableIncomeResponse])
async def list_variable_incomes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Income).where(Income.user_id == current_user.id)
    )
    income = result.scalar_one_or_none()
    
    if not income:
        return []
    
    result = await db.execute(
        select(VariableIncome).where(VariableIncome.income_id == income.id)
    )
    return result.scalars().all()


@router.post("/variable/", response_model=VariableIncomeResponse, status_code=201)
async def create_variable_income(
    variable_income_in: VariableIncomeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Income).where(Income.user_id == current_user.id)
    )
    income = result.scalar_one_or_none()
    
    if not income:
        income = Income(user_id=current_user.id)
        db.add(income)
        await db.commit()
        await db.refresh(income)
    
    variable_income = VariableIncome(**variable_income_in.dict(), income_id=income.id)
    db.add(variable_income)
    await db.commit()
    await db.refresh(variable_income)
    return variable_income


@router.put("/variable/{variable_income_id}/", response_model=VariableIncomeResponse)
async def update_variable_income(
    variable_income_id: int,
    variable_income_update: VariableIncomeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Income).where(Income.user_id == current_user.id)
    )
    income = result.scalar_one_or_none()
    if not income:
        raise HTTPException(status_code=404, detail="Configuração de receitas não encontrada")
    
    result = await db.execute(
        select(VariableIncome).where(
            VariableIncome.id == variable_income_id,
            VariableIncome.income_id == income.id
        )
    )
    variable_income = result.scalar_one_or_none()
    if not variable_income:
        raise HTTPException(status_code=404, detail="Receita variável não encontrada")
    
    for key, value in variable_income_update.dict().items():
        setattr(variable_income, key, value)
    
    await db.commit()
    await db.refresh(variable_income)
    return variable_income


@router.delete("/variable/{variable_income_id}/")
async def delete_variable_income(
    variable_income_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Income).where(Income.user_id == current_user.id)
    )
    income = result.scalar_one_or_none()
    if not income:
        raise HTTPException(status_code=404, detail="Configuração de receitas não encontrada")
    
    result = await db.execute(
        select(VariableIncome).where(
            VariableIncome.id == variable_income_id,
            VariableIncome.income_id == income.id
        )
    )
    variable_income = result.scalar_one_or_none()
    if not variable_income:
        raise HTTPException(status_code=404, detail="Receita variável não encontrada")
    
    await db.delete(variable_income)
    await db.commit()
    return {"message": "Receita variável removida com sucesso"}


@router.get("/fixed/", response_model=List[FixedIncomeResponse])
async def list_fixed_incomes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(FixedIncome).where(FixedIncome.user_id == current_user.id)
    )
    return result.scalars().all()


@router.post("/fixed/", response_model=FixedIncomeResponse, status_code=201)
async def create_fixed_income(
    fixed_income_in: FixedIncomeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    fixed_income = FixedIncome(**fixed_income_in.dict(), user_id=current_user.id)
    db.add(fixed_income)
    await db.commit()
    await db.refresh(fixed_income)
    return fixed_income


@router.put("/fixed/{fixed_income_id}/", response_model=FixedIncomeResponse)
async def update_fixed_income(
    fixed_income_id: int,
    fixed_income_update: FixedIncomeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(FixedIncome).where(
            FixedIncome.id == fixed_income_id,
            FixedIncome.user_id == current_user.id
        )
    )
    fixed_income = result.scalar_one_or_none()
    if not fixed_income:
        raise HTTPException(status_code=404, detail="Receita fixa não encontrada")

    for key, value in fixed_income_update.dict().items():
        setattr(fixed_income, key, value)

    await db.commit()
    await db.refresh(fixed_income)
    return fixed_income


@router.delete("/fixed/{fixed_income_id}/")
async def delete_fixed_income(
    fixed_income_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(FixedIncome).where(
            FixedIncome.id == fixed_income_id,
            FixedIncome.user_id == current_user.id
        )
    )
    fixed_income = result.scalar_one_or_none()
    if not fixed_income:
        raise HTTPException(status_code=404, detail="Receita fixa não encontrada")

    await db.delete(fixed_income)
    await db.commit()
    return {"message": "Receita fixa removida com sucesso"}

