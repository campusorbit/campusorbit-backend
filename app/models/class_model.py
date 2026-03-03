"""Class/Section Model for academic organization."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Class(Base):
    """Class/Section model for organizing students."""
    
    __tablename__ = "classes"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "Class 10"
    grade_level: Mapped[int] = mapped_column(Integer, nullable=False, index=True)  # 1-12
    section: Mapped[str | None] = mapped_column(String(10), nullable=True)  # A, B, C
    
    # Academic Year
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # "2024-2025"
    
    # Capacity
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True, default=40)
    
    # Class Teacher
    class_teacher_id: Mapped[str | None] = mapped_column(String(50), ForeignKey("users.id"), nullable=True, index=True)
    
    # Multi-campus Support
    campus_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    class_teacher: Mapped["User"] = relationship("User", foreign_keys=[class_teacher_id])  # type: ignore
