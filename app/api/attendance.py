import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.attendance import Attendance, BiometricRecord
from app.models.user import User
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceReport,
    AttendanceResponse,
    BiometricRecordCreate,
    BiometricRecordResponse,
)
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.get("/", response_model=list[AttendanceResponse])
async def list_attendance(
    student_id: str | None = Query(None),
    date: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(Attendance)
    if student_id:
        query = query.where(Attendance.student_id == student_id)
    if date:
        query = query.where(Attendance.date == date)
    result = await db.execute(query.order_by(Attendance.date.desc()).limit(100))
    return result.scalars().all()


@router.post("/", response_model=AttendanceResponse, status_code=201)
async def mark_attendance(
    data: AttendanceCreate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)
):
    record = Attendance(id=str(uuid.uuid4()), **data.model_dump())
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


@router.get("/report", response_model=AttendanceReport)
async def get_attendance_report(
    student_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    total = (await db.execute(select(func.count(Attendance.id)).where(Attendance.student_id == student_id))).scalar() or 0
    present = (await db.execute(select(func.count(Attendance.id)).where(Attendance.student_id == student_id, Attendance.status == "present"))).scalar() or 0
    absent = (await db.execute(select(func.count(Attendance.id)).where(Attendance.student_id == student_id, Attendance.status == "absent"))).scalar() or 0
    late = (await db.execute(select(func.count(Attendance.id)).where(Attendance.student_id == student_id, Attendance.status == "late"))).scalar() or 0
    percentage = (present / total * 100) if total > 0 else 0

    return AttendanceReport(total_days=total, present=present, absent=absent, late=late, percentage=round(percentage, 1))


@router.get("/biometric", response_model=list[BiometricRecordResponse])
async def list_biometric(
    teacher_id: str | None = Query(None),
    date: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(BiometricRecord)
    if teacher_id:
        query = query.where(BiometricRecord.teacher_id == teacher_id)
    if date:
        query = query.where(BiometricRecord.date == date)
    result = await db.execute(query.order_by(BiometricRecord.date.desc()).limit(100))
    return result.scalars().all()


@router.post("/biometric", response_model=BiometricRecordResponse, status_code=201)
async def log_biometric(
    data: BiometricRecordCreate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)
):
    record = BiometricRecord(id=str(uuid.uuid4()), **data.model_dump())
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record
