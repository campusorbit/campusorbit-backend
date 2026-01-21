from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Attendance(Base):
    __tablename__ = "attendance"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    student_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), nullable=False)
    date: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # present, absent, late
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    student: Mapped["User"] = relationship(back_populates="attendance_records", foreign_keys=[student_id])  # type: ignore[name-defined]


class BiometricRecord(Base):
    __tablename__ = "biometric_records"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    teacher_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), nullable=False)
    date: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    check_in: Mapped[str] = mapped_column(String(10), nullable=False)
    check_out: Mapped[str | None] = mapped_column(String(10), nullable=True)
    hours_worked: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    teacher: Mapped["User"] = relationship(foreign_keys=[teacher_id])  # type: ignore[name-defined]
