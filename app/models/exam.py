from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    course_id: Mapped[str] = mapped_column(String(50), ForeignKey("courses.id"), nullable=False)
    course_name: Mapped[str] = mapped_column(String(255), nullable=False)
    exam_type: Mapped[str] = mapped_column(String(50), nullable=False)  # midterm, endterm, quiz, assignment, online
    date: Mapped[str] = mapped_column(String(20), nullable=False)
    duration_mins: Mapped[int] = mapped_column(Integer, nullable=False)
    total_marks: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="scheduled")  # scheduled, ongoing, completed
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    results: Mapped[list["ExamResult"]] = relationship(back_populates="exam")


class ExamResult(Base):
    __tablename__ = "exam_results"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    exam_id: Mapped[str] = mapped_column(String(50), ForeignKey("exams.id"), nullable=False)
    student_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), nullable=False)
    student_name: Mapped[str] = mapped_column(String(255), nullable=False)
    marks_obtained: Mapped[float] = mapped_column(Float, nullable=False)
    total_marks: Mapped[int] = mapped_column(Integer, nullable=False)
    percentage: Mapped[float] = mapped_column(Float, nullable=False)
    grade: Mapped[str | None] = mapped_column(String(5), nullable=True)
    remarks: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    exam: Mapped["Exam"] = relationship(back_populates="results")
