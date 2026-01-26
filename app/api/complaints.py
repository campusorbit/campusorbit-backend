import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.complaint import Complaint
from app.models.user import User
from app.schemas.campus import ComplaintCreate, ComplaintResponse, ComplaintUpdate
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/complaints", tags=["Complaints"])


@router.get("/", response_model=list[ComplaintResponse])
async def list_complaints(
    status_filter: str | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Complaint)
    # Non-admin users can only see their own complaints
    if current_user.role.value not in ("admin", "employee"):
        query = query.where(Complaint.user_id == current_user.id)
    if status_filter:
        query = query.where(Complaint.status == status_filter)
    result = await db.execute(query.order_by(Complaint.created_at.desc()).limit(100))
    return result.scalars().all()


@router.post("/", response_model=ComplaintResponse, status_code=201)
async def create_complaint(
    data: ComplaintCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    complaint = Complaint(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        status="open",
        **data.model_dump(),
    )
    db.add(complaint)
    await db.flush()
    await db.refresh(complaint)
    return complaint


@router.put("/{complaint_id}", response_model=ComplaintResponse)
async def update_complaint(
    complaint_id: str,
    data: ComplaintUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Complaint).where(Complaint.id == complaint_id))
    complaint = result.scalar_one_or_none()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    # Only the author or admin can update
    if complaint.user_id != current_user.id and current_user.role.value not in ("admin", "employee"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(complaint, field, value)
    await db.flush()
    await db.refresh(complaint)
    return complaint
