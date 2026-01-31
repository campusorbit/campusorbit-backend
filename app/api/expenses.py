import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.expense import Budget, Expense
from app.models.user import User
from app.schemas.erp_modules import BudgetResponse, ExpenseCreate, ExpenseResponse
from app.services.auth_service import require_roles

router = APIRouter(prefix="/expenses", tags=["Expenses & Budget"])


@router.get("/", response_model=list[ExpenseResponse])
async def list_expenses(
    category: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles("admin", "finance_officer")),
):
    query = select(Expense).order_by(Expense.date.desc())
    if category:
        query = query.where(Expense.category == category)
    if status:
        query = query.where(Expense.status == status)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=ExpenseResponse, status_code=201)
async def create_expense(
    data: ExpenseCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles("admin", "finance_officer")),
):
    expense = Expense(id=str(uuid.uuid4()), status="pending", **data.model_dump())
    db.add(expense)
    await db.flush()
    await db.refresh(expense)
    return expense


@router.get("/budgets", response_model=list[BudgetResponse])
async def list_budgets(
    academic_year: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles("admin", "finance_officer")),
):
    query = select(Budget).order_by(Budget.category)
    if academic_year:
        query = query.where(Budget.academic_year == academic_year)
    result = await db.execute(query)
    return result.scalars().all()
