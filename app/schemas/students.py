"""Schemas for Student Information System."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ========== Student Profile Schemas ==========

class StudentProfileBase(BaseModel):
    """Base schema for student profile."""
    admission_number: str = Field(..., min_length=1, max_length=50)
    admission_date: date
    batch_year: int = Field(..., ge=1900, le=2100)
    class_id: Optional[str] = None
    section: Optional[str] = Field(None, max_length=10)
    guardian_name: str = Field(..., min_length=1, max_length=255)
    guardian_email: Optional[EmailStr] = None
    guardian_phone: str = Field(..., min_length=10, max_length=20)
    guardian_relationship: Optional[str] = Field(None, max_length=50)
    previous_school: Optional[str] = Field(None, max_length=255)
    previous_school_grade: Optional[str] = Field(None, max_length=50)
    blood_group: Optional[str] = Field(None, max_length=5)
    medical_conditions: Optional[str] = None
    allergies: Optional[str] = None
    bio: Optional[str] = None
    sibling_info: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(default="India", max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    emergency_contact_name: Optional[str] = Field(None, max_length=255)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=50)
    campus_id: Optional[str] = None


class StudentProfileCreate(StudentProfileBase):
    """Schema for creating student profile."""
    student_id: str


class StudentProfileUpdate(BaseModel):
    """Schema for updating student profile."""
    class_id: Optional[str] = None
    section: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_email: Optional[EmailStr] = None
    guardian_phone: Optional[str] = None
    guardian_relationship: Optional[str] = None
    previous_school: Optional[str] = None
    previous_school_grade: Optional[str] = None
    blood_group: Optional[str] = None
    medical_conditions: Optional[str] = None
    allergies: Optional[str] = None
    bio: Optional[str] = None
    sibling_info: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None


class StudentProfileResponse(StudentProfileBase):
    """Schema for student profile response."""
    id: str
    student_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== Student Schemas ==========

class StudentBase(BaseModel):
    """Base schema for student."""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    roll_no: Optional[str] = Field(None, max_length=50)
    parent_name: Optional[str] = Field(None, max_length=255)
    parent_phone: Optional[str] = Field(None, max_length=20)


class StudentCreate(StudentBase):
    """Schema for creating a student."""
    password: str = Field(..., min_length=8)
    
    # Student profile fields
    admission_number: str
    admission_date: date
    batch_year: int = Field(..., ge=1900, le=2100)
    class_id: Optional[str] = None
    section: Optional[str] = None
    guardian_name: str
    guardian_email: Optional[EmailStr] = None
    guardian_phone: str
    guardian_relationship: Optional[str] = None
    blood_group: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = Field(default="India")
    postal_code: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None


class StudentUpdate(BaseModel):
    """Schema for updating a student."""
    name: Optional[str] = None
    phone: Optional[str] = None
    roll_no: Optional[str] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None


class StudentResponse(BaseModel):
    """Schema for student response."""
    id: str
    email: str
    name: str
    role: str
    phone: Optional[str] = None
    roll_no: Optional[str] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StudentDetailResponse(StudentResponse):
    """Schema for detailed student response with profile."""
    profile: Optional[StudentProfileResponse] = None


# ========== Class Schemas ==========

class ClassBase(BaseModel):
    """Base schema for class."""
    name: str = Field(..., min_length=1, max_length=100)
    grade_level: int = Field(..., ge=1, le=12)
    section: Optional[str] = Field(None, max_length=10)
    academic_year: str = Field(..., pattern=r"^\d{4}-\d{4}$")
    capacity: Optional[int] = Field(None, ge=1, le=200)
    class_teacher_id: Optional[str] = None
    campus_id: Optional[str] = None


class ClassCreate(ClassBase):
    """Schema for creating a class."""
    pass


class ClassUpdate(BaseModel):
    """Schema for updating a class."""
    name: Optional[str] = None
    section: Optional[str] = None
    capacity: Optional[int] = None
    class_teacher_id: Optional[str] = None
    is_active: Optional[bool] = None


class ClassResponse(ClassBase):
    """Schema for class response."""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== List Responses ==========

class StudentListResponse(BaseModel):
    """Schema for list of students."""
    total: int
    students: list[StudentResponse]


class StudentSearchParams(BaseModel):
    """Schema for student search parameters."""
    search: Optional[str] = None
    class_id: Optional[str] = None
    batch_year: Optional[int] = None
    section: Optional[str] = None
    is_active: Optional[bool] = True
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


# ========== Summary Schemas ==========

class AttendanceSummary(BaseModel):
    """Schema for attendance summary."""
    total_days: int
    present_days: int
    absent_days: int
    late_days: int
    attendance_percentage: float


class FeeHistoryItem(BaseModel):
    """Schema for fee history item."""
    id: str
    fee_type: str
    amount: float
    paid_amount: float
    due_date: date
    status: str
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentItem(BaseModel):
    """Schema for document item."""
    id: str
    document_type: str
    file_name: str
    file_url: str
    uploaded_at: datetime

    class Config:
        from_attributes = True
