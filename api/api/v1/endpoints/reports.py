# app/api/v1/endpoints/reports.py
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, extract, func
from typing import Optional
from decimal import Decimal
from io import BytesIO
from datetime import date
import calendar
from dateutil.relativedelta import relativedelta

from api.db.session import get_db
from api.models.user import User
from api.models.expense import Expense, ExpenseType
from api.models.income import Income, VariableIncome, FixedIncome
from api.models.fixed_expense import FixedExpense
from api.schemas.reports import ReportRequest, ReportEmailRequest
from api.api.deps import get_current_user
from api.services.pdf_service import generate_report_pdf
from api.services.email_service import send_report_email

router = APIRouter()


@router.get("/generate/")
async def generate_report(
    type: str = Query(..., description="Tipo do relatório: mensal, anual, categoria"),
    category_id: Optional[int] = None,
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000),
    start_date: Optional[date] = Query(None, description="Data de início para filtro (formato YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Data de fim para filtro (formato YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Expense).where(Expense.user_id == current_user.id)

    # Apply date filtering
    if start_date and end_date:
        query = query.where(Expense.date.between(start_date, end_date))
    else:
        if type == "mensal" and month and year:
            query = query.where(
                extract('month', Expense.date) == month,
                extract('year', Expense.date) == year
            )
        elif type == "anual" and year:
            query = query.where(extract('year', Expense.date) == year)
        elif type == "categoria" and category_id and month and year:
            query = query.where(
                Expense.category_id == category_id,
                extract('month', Expense.date) == month,
                extract('year', Expense.date) == year
            )

    result = await db.execute(query)
    expenses = result.scalars().all()

    # Query fixed expenses with date filtering
    fixed_expenses_query = select(FixedExpense).where(
        FixedExpense.user_id == current_user.id,
        FixedExpense.is_active == True
    )

    if start_date and end_date:
        # For custom date range, include all active fixed expenses (they repeat monthly)
        pass
    elif type == "mensal" and month and year:
        # For monthly reports, include all active fixed expenses (they are monthly)
        pass  # No additional filter needed
    elif type == "anual" and year:
        # For annual reports, include all active fixed expenses
        pass  # No additional filter needed
    elif type == "categoria" and category_id and month and year:
        # For category reports, filter by category and include all for the month
        fixed_expenses_query = fixed_expenses_query.where(FixedExpense.category_id == category_id)

    result_fixed = await db.execute(fixed_expenses_query)
    fixed_expenses = result_fixed.scalars().all()

    # Determine report start and end dates
    if start_date and end_date:
        report_start = start_date
        report_end = end_date
    elif type == "mensal" and month and year:
        report_start = date(year, month, 1)
        report_end = date(year, month, calendar.monthrange(year, month)[1])
    elif type == "anual" and year:
        report_start = date(year, 1, 1)
        report_end = date(year, 12, 31)
    elif type == "categoria" and category_id and month and year:
        report_start = date(year, month, 1)
        report_end = date(year, month, calendar.monthrange(year, month)[1])
    else:
        today = date.today()
        report_start = date(today.year, today.month, 1)
        report_end = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])

    # Calculate fixed expenses multiplier and date function
    if type == "anual" and year:
        fixed_multiplier = 12
        fixed_date_func = lambda fe: date(year, 1, fe.day_of_month)
    elif (type == "mensal" or type == "categoria") and month and year:
        fixed_multiplier = 1
        fixed_date_func = lambda fe: date(year, month, fe.day_of_month)
    elif start_date and end_date:
        fixed_multiplier = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month + 1
        fixed_date_func = lambda fe: start_date
    else:
        fixed_multiplier = 1
        fixed_date_func = lambda fe: date.today()

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

    fixed_expenses_sum = sum(fe.amount for fe in fixed_expenses)
    total_expense += fixed_multiplier * fixed_expenses_sum

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

    # Add fixed expense transactions for each month in the period
    current_date = report_start
    while current_date <= report_end:
        for fe in fixed_expenses:
            if category_id is None or fe.category_id == category_id:
                # Determine the day for this month, adjusting if necessary
                try:
                    trans_date = date(current_date.year, current_date.month, fe.day_of_month)
                except ValueError:
                    # If day_of_month is invalid for the month, use the last day
                    last_day = calendar.monthrange(current_date.year, current_date.month)[1]
                    trans_date = date(current_date.year, current_date.month, last_day)
                transactions.append({
                    "id": fe.id,
                    "description": fe.description,
                    "amount": fe.amount,
                    "type": "despesa",
                    "date": trans_date,
                    "category_id": fe.category_id
                })
        current_date += relativedelta(months=1)

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
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    report_data = await generate_report(type, category_id, month, year, start_date, end_date, current_user, db)
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
        report_request.start_date,
        report_request.end_date,
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

