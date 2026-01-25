import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.course import Assignment, Course, Grade, StudyMaterial, Syllabus
from app.models.user import User
from app.redis import get_cached, invalidate_cache, set_cached
from app.schemas.course import (
    AssignmentCreate,
    AssignmentResponse,
    CourseCreate,
    CourseResponse,
    GradeCreate,
    GradeResponse,
    StudyMaterialCreate,
    StudyMaterialResponse,
    SyllabusCreate,
    SyllabusResponse,
)
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("/", response_model=list[CourseResponse])
async def list_courses(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    cached = await get_cached("courses:all")
    if cached:
        return cached

    result = await db.execute(select(Course).order_by(Course.code))
    courses = result.scalars().all()
    response = []
    for c in courses:
        instructor = await db.execute(select(User.name).where(User.id == c.instructor_id))
        name = instructor.scalar_one_or_none()
        resp = CourseResponse.model_validate(c)
        resp.instructor_name = name
        response.append(resp)

    await set_cached("courses:all", [r.model_dump() for r in response], ttl=120)
    return response


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(data: CourseCreate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    course = Course(id=str(uuid.uuid4()), **data.model_dump())
    db.add(course)
    await db.flush()
    await db.refresh(course)
    await invalidate_cache("courses:*")
    return course


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: str, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    resp = CourseResponse.model_validate(course)
    instructor = await db.execute(select(User.name).where(User.id == course.instructor_id))
    resp.instructor_name = instructor.scalar_one_or_none()
    return resp


# --- Assignments ---
@router.get("/{course_id}/assignments", response_model=list[AssignmentResponse])
async def list_assignments(course_id: str, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    result = await db.execute(
        select(Assignment).where(Assignment.course_id == course_id).order_by(Assignment.due_date)
    )
    return result.scalars().all()


@router.post("/{course_id}/assignments", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    course_id: str, data: AssignmentCreate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)
):
    assignment = Assignment(id=str(uuid.uuid4()), course_id=course_id, **data.model_dump())
    db.add(assignment)
    await db.flush()
    await db.refresh(assignment)
    return assignment


# --- Grades ---
@router.get("/{course_id}/grades", response_model=list[GradeResponse])
async def list_grades(course_id: str, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    result = await db.execute(select(Grade).where(Grade.course_id == course_id))
    return result.scalars().all()


@router.post("/{course_id}/grades", response_model=GradeResponse, status_code=status.HTTP_201_CREATED)
async def create_grade(
    course_id: str, data: GradeCreate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)
):
    grade = Grade(id=str(uuid.uuid4()), course_id=course_id, **data.model_dump())
    db.add(grade)
    await db.flush()
    await db.refresh(grade)
    return grade


# --- Study Materials ---
@router.get("/{course_id}/materials", response_model=list[StudyMaterialResponse])
async def list_materials(course_id: str, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    result = await db.execute(
        select(StudyMaterial).where(StudyMaterial.course_id == course_id).order_by(StudyMaterial.uploaded_date.desc())
    )
    return result.scalars().all()


@router.post("/{course_id}/materials", response_model=StudyMaterialResponse, status_code=status.HTTP_201_CREATED)
async def create_material(
    course_id: str, data: StudyMaterialCreate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)
):
    material = StudyMaterial(id=str(uuid.uuid4()), course_id=course_id, **data.model_dump())
    db.add(material)
    await db.flush()
    await db.refresh(material)
    return material


# --- Syllabus ---
@router.get("/{course_id}/syllabus", response_model=list[SyllabusResponse])
async def list_syllabus(course_id: str, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    result = await db.execute(
        select(Syllabus).where(Syllabus.course_id == course_id).order_by(Syllabus.unit_number)
    )
    return result.scalars().all()


@router.post("/{course_id}/syllabus", response_model=SyllabusResponse, status_code=status.HTTP_201_CREATED)
async def create_syllabus_item(
    course_id: str, data: SyllabusCreate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)
):
    item = Syllabus(id=str(uuid.uuid4()), course_id=course_id, **data.model_dump())
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item
