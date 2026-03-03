"""Student Profile Model - Extended student information."""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StudentProfile(Base):
    """Extended student profile information."""
    
    __tablename__ = "student_profiles"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    student_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), unique=True, nullable=False, index=True)
    
    # Admission Information
    admission_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    admission_date: Mapped[date] = mapped_column(Date, nullable=False)
    batch_year: Mapped[int] = mapped_column(nullable=False, index=True)
    
    # Academic Information
    class_id: Mapped[str | None] = mapped_column(String(50), ForeignKey("classes.id"), nullable=True, index=True)
    section: Mapped[str | None] = mapped_column(String(10), nullable=True)
    
    # Guardian Information
    guardian_name: Mapped[str] = mapped_column(String(255), nullable=False)
    guardian_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    guardian_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    guardian_relationship: Mapped[str | None] = mapped_column(String(50), nullable=True)  # father/mother/guardian
    
    # Previous Education
    previous_school: Mapped[str | None] = mapped_column(String(255), nullable=True)
    previous_school_grade: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Medical Information
    blood_group: Mapped[str | None] = mapped_column(String(5), nullable=True)
    medical_conditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    allergies: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Additional Information
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    sibling_info: Mapped[str | None] = mapped_column(Text, nullable=True)  # Can be JSON in future
    
    # Address
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True, default="India")
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    
    # Emergency Contact
    emergency_contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    emergency_contact_relationship: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Multi-campus Support
    campus_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    student: Mapped["User"] = relationship("User", foreign_keys=[student_id], back_populates="profile")  # type: ignore
