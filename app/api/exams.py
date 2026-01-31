import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.exam import Exam, ExamResult
from app.models.user import User
from app.schemas.erp_modules import ExamCreate, ExamResponse, ExamResultResponse
from app.services.auth_service import get_current_user, require_roles

router = APIRouter(prefix="/exams", tags=["Exams & Assessments"])


@router.get("/", response_model=list[ExamResponse])
async def list_exams(
    course_id: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(Exam).order_by(Exam.date.desc())
    if course_id:
        query = query.where(Exam.course_id == course_id)
    if status:
        query = query.where(Exam.status == status)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=ExamResponse, status_code=201)
async def create_exam(
    data: ExamCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles("admin", "teacher")),
):
    exam = Exam(id=str(uuid.uuid4()), status="scheduled", **data.model_dump())
    db.add(exam)
    await db.flush()
    await db.refresh(exam)
    return exam


@router.get("/{exam_id}/results", response_model=list[ExamResultResponse])
async def list_results(
    exam_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(ExamResult).where(ExamResult.exam_id == exam_id)
    # Students can only see their own results
    if current_user.role.value == "student":
        query = query.where(ExamResult.student_id == current_user.id)
    result = await db.execute(query.order_by(ExamResult.student_name))
    return result.scalars().all()
