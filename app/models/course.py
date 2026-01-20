from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    instructor_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), nullable=False)
    semester: Mapped[str] = mapped_column(String(50), nullable=False)
    credits: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    student_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    instructor: Mapped["User"] = relationship(foreign_keys=[instructor_id])  # type: ignore[name-defined]
    assignments: Mapped[list["Assignment"]] = relationship(back_populates="course", cascade="all, delete-orphan")
    grades: Mapped[list["Grade"]] = relationship(back_populates="course", cascade="all, delete-orphan")
    materials: Mapped[list["StudyMaterial"]] = relationship(back_populates="course", cascade="all, delete-orphan")
    syllabus_items: Mapped[list["Syllabus"]] = relationship(back_populates="course", cascade="all, delete-orphan")


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    course_id: Mapped[str] = mapped_column(String(50), ForeignKey("courses.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[str] = mapped_column(String(20), nullable=False)
    submitted_by: Mapped[int] = mapped_column(Integer, default=0)
    total_students: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    course: Mapped["Course"] = relationship(back_populates="assignments")


class Grade(Base):
    __tablename__ = "grades"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    student_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), nullable=False)
    course_id: Mapped[str] = mapped_column(String(50), ForeignKey("courses.id"), nullable=False)
    midterm: Mapped[float | None] = mapped_column(nullable=True)
    endterm: Mapped[float | None] = mapped_column(nullable=True)
    assignment_score: Mapped[float | None] = mapped_column(nullable=True)
    grade_letter: Mapped[str | None] = mapped_column(String(5), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    student: Mapped["User"] = relationship(back_populates="grades", foreign_keys=[student_id])  # type: ignore[name-defined]
    course: Mapped["Course"] = relationship(back_populates="grades")


class StudyMaterial(Base):
    __tablename__ = "study_materials"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    course_id: Mapped[str] = mapped_column(String(50), ForeignKey("courses.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # pdf, video, pptx
    uploaded_date: Mapped[str] = mapped_column(String(20), nullable=False)
    size: Mapped[str] = mapped_column(String(20), nullable=False)
    downloads: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    course: Mapped["Course"] = relationship(back_populates="materials")


class Syllabus(Base):
    __tablename__ = "syllabus"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    course_id: Mapped[str] = mapped_column(String(50), ForeignKey("courses.id"), nullable=False)
    unit_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    topics: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array as text
    hours: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    course: Mapped["Course"] = relationship(back_populates="syllabus_items")
