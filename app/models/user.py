import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    teacher = "teacher"
    student = "student"
    parent = "parent"
    finance_officer = "finance_officer"
    employee = "employee"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, index=True)
    avatar: Mapped[str | None] = mapped_column(String(50), nullable=True)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    join_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    roll_no: Mapped[str | None] = mapped_column(String(50), nullable=True)
    specialization: Mapped[str | None] = mapped_column(String(255), nullable=True)
    qualifications: Mapped[str | None] = mapped_column(String(500), nullable=True)
    experience: Mapped[str | None] = mapped_column(String(100), nullable=True)
    parent_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    parent_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    cgpa: Mapped[float | None] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    fees: Mapped[list["Fee"]] = relationship(back_populates="student", foreign_keys="Fee.student_id")  # type: ignore[name-defined]
    grades: Mapped[list["Grade"]] = relationship(back_populates="student", foreign_keys="Grade.student_id")  # type: ignore[name-defined]
    attendance_records: Mapped[list["Attendance"]] = relationship(back_populates="student", foreign_keys="Attendance.student_id")  # type: ignore[name-defined]
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")  # type: ignore[name-defined]
    complaints: Mapped[list["Complaint"]] = relationship(back_populates="user")  # type: ignore[name-defined]
