# app/api/v1/endpoints/reports.py
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, extract, func
from typing import Optional
from decimal import Decimal
from io import BytesIO

from app.db.session import get_db
from app.models.user import User
from app.models.expense import Expense, ExpenseType
from app.models.income import Income, VariableIncome, FixedIncome
from app.schemas.reports import ReportRequest, ReportEmailRequest
from app.api.deps import get_current_user
from app.services.pdf_service import generate_report_pdf
from app.services.email_service import send_report_email

router = APIRouter()


@router.get("/generate/")
async def generate_report(
    type: str = Query(..., description="Tipo do relatório: mensal, anual, categoria"),
    category_id: Optional[int] = None,
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Expense).where(Expense.user_id == current_user.id)

    if type == "mensal":
        query = query.where(
            extract('month', Expense.date) == month,
            extract('year', Expense.date) == year
        )
    elif type == "anual":
        query = query.where(extract('year', Expense.date) == year)
    elif type == "categoria" and category_id:
        query = query.where(
            Expense.category_id == category_id,
            extract('month', Expense.date) == month,
            extract('year', Expense.date) == year
        )

    result = await db.execute(query)
    expenses = result.scalars().all()

    # Calcular total de entradas (receitas)
    # Receitas fixas mensais (Income.fixed_amount)
    result_income = await db.execute(
        select(Income).where(Income.user_id == current_user.id)
    )
    income_config = result_income.scalar_one_or_none()
    fixed_monthly_income = income_config.fixed_amount if income_config else 0

    # Receitas variáveis ativas (VariableIncome)
    result_var = await db.execute(
        select(func.sum(VariableIncome.amount))
        .join(Income, VariableIncome.income_id == Income.id)
        .where(
            Income.user_id == current_user.id,
            VariableIncome.is_active == True
        )
    )
    variable_income = result_var.scalar() or 0

    # Receitas fixas adicionais (FixedIncome)
    result_fixed = await db.execute(
        select(func.sum(FixedIncome.amount)).where(
            FixedIncome.user_id == current_user.id,
            FixedIncome.is_active == True
        )
    )
    fixed_incomes = result_fixed.scalar() or 0

    # Receitas via Expense do período
    monthly_expense_income = sum(e.amount for e in expenses if e.type == ExpenseType.RECEITA)

    # Total de entradas = renda fixa mensal + variáveis ativas + fixas adicionais + receitas via expenses do período
    total_income = fixed_monthly_income + variable_income + fixed_incomes + monthly_expense_income

    # Total de saídas (despesas)
    total_expense = sum(e.amount for e in expenses if e.type == ExpenseType.DESPESA)

    # Fetch VariableIncome records
    result_var_incomes = await db.execute(
        select(VariableIncome)
        .join(Income, VariableIncome.income_id == Income.id)
        .where(
            Income.user_id == current_user.id,
            VariableIncome.is_active == True
        )
    )
    variable_incomes_list = result_var_incomes.scalars().all()

    # Fetch FixedIncome records
    result_fixed_incomes = await db.execute(
        select(FixedIncome).where(
            FixedIncome.user_id == current_user.id,
            FixedIncome.is_active == True
        )
    )
    fixed_incomes_list = result_fixed_incomes.scalars().all()

    # Build transactions list including expenses and incomes
    transactions = []

    # Add expense transactions
    for e in expenses:
        transactions.append({
            "id": e.id,
            "description": e.description,
            "amount": e.amount,
            "type": e.type.value,
            "date": e.date,
            "category_id": e.category_id
        })

    # Add variable income transactions
    for vi in variable_incomes_list:
        transactions.append({
            "id": vi.id,
            "description": vi.description,
            "amount": vi.amount,
            "type": "receita",
            "date": vi.created_at.date(),
            "category_id": None
        })

    # Add fixed income transactions
    for fi in fixed_incomes_list:
        transactions.append({
            "id": fi.id,
            "description": fi.description,
            "amount": fi.amount,
            "type": "receita",
            "date": fi.created_at.date(),
            "category_id": None
        })

    return {
        "type": type,
        "month": month,
        "year": year,
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense,
        "transactions": transactions
    }


@router.get("/pdf/")
async def generate_pdf_report(
    type: str = Query(...),
    category_id: Optional[int] = None,
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    report_data = await generate_report(type, category_id, month, year, current_user, db)
    pdf_buffer = generate_report_pdf(report_data, current_user.name)
    
    return StreamingResponse(
        BytesIO(pdf_buffer),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=relatorio_{month}_{year}.pdf"}
    )


@router.post("/email/")
async def email_report(
    report_request: ReportEmailRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    report_data = await generate_report(
        report_request.type,
        report_request.category_id,
        report_request.month,
        report_request.year,
        current_user,
        db
    )
    
    pdf_buffer = generate_report_pdf(report_data, current_user.name)
    
    await send_report_email(
        to_email=report_request.email,
        user_name=current_user.name,
        pdf_buffer=pdf_buffer,
        month=report_request.month,
        year=report_request.year
    )
    
    return {"message": "Relatório enviado por email com sucesso"}

