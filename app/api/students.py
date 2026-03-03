"""API endpoints for Student Information System."""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.models.user import User, UserRole
from app.models.student_profile import StudentProfile
from app.models.class_model import Class
from app.models.attendance import Attendance
from app.models.fee import Fee
from app.models.document import Document
from app.schemas.students import (
    AttendanceSummary,
    ClassCreate,
    ClassResponse,
    ClassUpdate,
    DocumentItem,
    FeeHistoryItem,
    StudentCreate,
    StudentDetailResponse,
    StudentListResponse,
    StudentProfileCreate,
    StudentProfileResponse,
    StudentProfileUpdate,
    StudentResponse,
    StudentSearchParams,
    StudentUpdate,
)
from app.services.auth_service import get_current_user, hash_password, require_roles

router = APIRouter(prefix="/students", tags=["Students"])


# ========== Student CRUD Operations ==========

@router.get("/", response_model=StudentListResponse)
async def list_students(
    search: Optional[str] = Query(None),
    class_id: Optional[str] = Query(None),
    batch_year: Optional[int] = Query(None),
    section: Optional[str] = Query(None),  
    is_active: Optional[bool] = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher")),
):
    """List all students with optional filters."""
    query = select(User).where(User.role == UserRole.student)
    
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            (User.name.ilike(search_term)) |
            (User.email.ilike(search_term)) |
            (User.roll_no.ilike(search_term))
        )
    
    # Join with profile for additional filters
    if class_id or batch_year or section:
        query = query.join(StudentProfile, User.id == StudentProfile.student_id)
        if class_id:
            query = query.where(StudentProfile.class_id == class_id)
        if batch_year:
            query = query.where(StudentProfile.batch_year == batch_year)
        if section:
            query = query.where(StudentProfile.section == section)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Get paginated results
    query = query.offset(skip).limit(limit).order_by(User.name)
    result = await db.execute(query)
    students = result.scalars().all()
    
    return StudentListResponse(total=total, students=students)


@router.post("/", response_model=StudentDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_student(
    data: StudentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    """Create a new student with profile."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Check if admission number already exists
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.admission_number == data.admission_number)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Admission number already exists"
        )
    
    # Validate class_id if provided
    if data.class_id:
        result = await db.execute(select(Class).where(Class.id == data.class_id))
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found"
            )
    
    # Create user
    user = User(
        id=str(uuid.uuid4()),
        email=data.email,
        name=data.name,
        hashed_password=hash_password(data.password),
        role=UserRole.student,
        phone=data.phone,
        roll_no=data.roll_no,
        parent_name=data.parent_name or data.guardian_name,
        parent_phone=data.parent_phone or data.guardian_phone,
        is_active=True,
    )
    db.add(user)
    await db.flush()  # Get the user ID
    
    # Create student profile
    profile = StudentProfile(
        id=str(uuid.uuid4()),
        student_id=user.id,
        admission_number=data.admission_number,
        admission_date=data.admission_date,
        batch_year=data.batch_year,
        class_id=data.class_id,
        section=data.section,
        guardian_name=data.guardian_name,
        guardian_email=data.guardian_email,
        guardian_phone=data.guardian_phone,
        guardian_relationship=data.guardian_relationship,
        blood_group=data.blood_group,
        address=data.address,
        city=data.city,
        state=data.state,
        country=data.country or "India",
        postal_code=data.postal_code,
        emergency_contact_name=data.emergency_contact_name,
        emergency_contact_phone=data.emergency_contact_phone,
    )
    db.add(profile)
    
    await db.commit()
    await db.refresh(user)
    await db.refresh(profile)
    
    # Return user with profile
    response = StudentDetailResponse.model_validate(user)
    response.profile = StudentProfileResponse.model_validate(profile)
    return response


# ========== Class Management ==========

@router.post("/classes", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
async def create_class(
    data: ClassCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    """Create a new class/section."""
    # Validate class_teacher_id if provided
    if data.class_teacher_id:
        result = await db.execute(
            select(User).where(
                User.id == data.class_teacher_id,
                User.role == UserRole.teacher
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found"
            )
    
    # Create class
    class_obj = Class(
        id=str(uuid.uuid4()),
        name=data.name,
        grade_level=data.grade_level,
        section=data.section,
        academic_year=data.academic_year,
        capacity=data.capacity,
        class_teacher_id=data.class_teacher_id,
        campus_id=data.campus_id,
        is_active=True,
    )
    db.add(class_obj)
    
    await db.commit()
    await db.refresh(class_obj)
    return class_obj


@router.get("/classes", response_model=List[ClassResponse])
async def list_classes(
    grade_level: Optional[int] = Query(None, ge=1, le=12),
    academic_year: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all classes."""
    query = select(Class)
    
    if grade_level:
        query = query.where(Class.grade_level == grade_level)
    if academic_year:
        query = query.where(Class.academic_year == academic_year)
    if is_active is not None:
        query = query.where(Class.is_active == is_active)
    
    query = query.order_by(Class.grade_level, Class.section)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/classes/{class_id}", response_model=ClassResponse)
async def get_class(
    class_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get class details."""
    result = await db.execute(select(Class).where(Class.id == class_id))
    class_obj = result.scalar_one_or_none()
    
    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )
    
    return class_obj


@router.put("/classes/{class_id}", response_model=ClassResponse)
async def update_class(
    class_id: str,
    data: ClassUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    """Update class information."""
    result = await db.execute(select(Class).where(Class.id == class_id))
    class_obj = result.scalar_one_or_none()
    
    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )
    
    # Validate class_teacher_id if being updated
    if data.class_teacher_id:
        result = await db.execute(
            select(User).where(
                User.id == data.class_teacher_id,
                User.role == UserRole.teacher
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found"
            )
    
    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(class_obj, field, value)
    
    await db.commit()
    await db.refresh(class_obj)
    return class_obj


@router.delete("/classes/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_class(
    class_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    """Soft delete a class (deactivate)."""
    result = await db.execute(select(Class).where(Class.id == class_id))
    class_obj = result.scalar_one_or_none()
    
    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )
    
    class_obj.is_active = False
    await db.commit()


# ========== Student Detail Operations (parameterized routes) ==========

@router.get("/{student_id}", response_model=StudentDetailResponse)
async def get_student(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get student details with profile."""
    # Students can only see their own details, teachers and admins can see all
    if current_user.role == UserRole.student and current_user.id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this student"
        )
    
    result = await db.execute(
        select(User)
        .options(joinedload(User.profile))
        .where(User.id == student_id, User.role == UserRole.student)
    )
    student = result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    response = StudentDetailResponse.model_validate(student)
    if hasattr(student, 'profile') and student.profile:
        response.profile = StudentProfileResponse.model_validate(student.profile)
    return response


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: str,
    data: StudentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher")),
):
    """Update student basic information."""
    result = await db.execute(
        select(User).where(User.id == student_id, User.role == UserRole.student)
    )
    student = result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)
    
    await db.commit()
    await db.refresh(student)
    return student


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    """Soft delete a student (deactivate)."""
    result = await db.execute(
        select(User).where(User.id == student_id, User.role == UserRole.student)
    )
    student = result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    student.is_active = False
    await db.commit()


# ========== Student Profile Operations ==========

@router.get("/{student_id}/profile", response_model=StudentProfileResponse)
async def get_student_profile(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get extended student profile."""
    # Students can only see their own profile
    if current_user.role == UserRole.student and current_user.id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this profile"
        )
    
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.student_id == student_id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    return profile


@router.put("/{student_id}/profile", response_model=StudentProfileResponse)
async def update_student_profile(
    student_id: str,
    data: StudentProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher")),
):
    """Update extended student profile."""
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.student_id == student_id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    # Validate class_id if being updated
    if data.class_id:
        result = await db.execute(select(Class).where(Class.id == data.class_id))
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found"
            )
    
    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    await db.commit()
    await db.refresh(profile)
    return profile


# ========== Student Summary Endpoints ==========

@router.get("/{student_id}/attendance-summary", response_model=AttendanceSummary)
async def get_attendance_summary(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get student attendance summary."""
    # Students can only see their own attendance
    if current_user.role == UserRole.student and current_user.id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this attendance"
        )
    
    # Verify student exists
    result = await db.execute(
        select(User).where(User.id == student_id, User.role == UserRole.student)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Get attendance records
    result = await db.execute(
        select(Attendance).where(Attendance.student_id == student_id)
    )
    records = result.scalars().all()
    
    total_days = len(records)
    present_days = sum(1 for r in records if r.status == "present")
    absent_days = sum(1 for r in records if r.status == "absent")
    late_days = sum(1 for r in records if r.status == "late")
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0.0
    
    return AttendanceSummary(
        total_days=total_days,
        present_days=present_days,
        absent_days=absent_days,
        late_days=late_days,
        attendance_percentage=round(attendance_percentage, 2)
    )


@router.get("/{student_id}/fee-history", response_model=List[FeeHistoryItem])
async def get_fee_history(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get student fee payment history."""
    # Students can only see their own fees
    if current_user.role == UserRole.student and current_user.id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this fee history"
        )
    
    # Verify student exists
    result = await db.execute(
        select(User).where(User.id == student_id, User.role == UserRole.student)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Get fee records
    result = await db.execute(
        select(Fee)
        .where(Fee.student_id == student_id)
        .order_by(Fee.due_date.desc())
    )
    fees = result.scalars().all()
    
    return fees


@router.get("/{student_id}/documents", response_model=List[DocumentItem])
async def get_student_documents(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get student documents."""
    # Students can only see their own documents
    if current_user.role == UserRole.student and current_user.id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these documents"
        )
    
    # Verify student exists
    result = await db.execute(
        select(User).where(User.id == student_id, User.role == UserRole.student)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Get documents
    # NOTE: Simplified version for now - entity filtering will be added after DB migration
    result = await db.execute(
        select(Document).order_by(Document.created_at.desc()).limit(100)
    )
    documents = result.scalars().all()
    
    # Filter by student manually as a workaround
    return [
        doc for doc in documents 
        if (getattr(doc, 'entity_id', None) == student_id and 
            getattr(doc, 'entity_type', None) == "student")
    ]
