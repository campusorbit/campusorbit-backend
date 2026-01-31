import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.hr import LeaveRequest, SalarySlip
from app.models.user import User
from app.schemas.erp_modules import (
    LeaveRequestCreate,
    LeaveRequestResponse,
    LeaveRequestUpdate,
    SalarySlipResponse,
)
from app.services.auth_service import get_current_user, require_roles

router = APIRouter(prefix="/hr", tags=["HR & Payroll"])


@router.get("/salary-slips", response_model=list[SalarySlipResponse])
async def list_salary_slips(
    employee_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(SalarySlip).order_by(SalarySlip.year.desc(), SalarySlip.month.desc())
    # Non-admin users can only see their own slips
    if current_user.role.value not in ("admin", "finance_officer"):
        query = query.where(SalarySlip.employee_id == current_user.id)
    elif employee_id:
        query = query.where(SalarySlip.employee_id == employee_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/leaves", response_model=list[LeaveRequestResponse])
async def list_leaves(
    user_id: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(LeaveRequest).order_by(LeaveRequest.created_at.desc())
    # Non-admin/teacher users can only see their own leaves
    if current_user.role.value not in ("admin",):
        query = query.where(LeaveRequest.user_id == current_user.id)
    elif user_id:
        query = query.where(LeaveRequest.user_id == user_id)
    if status:
        query = query.where(LeaveRequest.status == status)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/leaves", response_model=LeaveRequestResponse, status_code=201)
async def create_leave(
    data: LeaveRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    leave = LeaveRequest(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        user_name=current_user.name,
        status="pending",
        **data.model_dump(),
    )
    db.add(leave)
    await db.flush()
    await db.refresh(leave)
    return leave


@router.put("/leaves/{leave_id}", response_model=LeaveRequestResponse)
async def update_leave(
    leave_id: str,
    data: LeaveRequestUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    result = await db.execute(select(LeaveRequest).where(LeaveRequest.id == leave_id))
    leave = result.scalar_one_or_none()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(leave, field, value)
    await db.flush()
    await db.refresh(leave)
    return leave
