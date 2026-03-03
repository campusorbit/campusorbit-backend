from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # Circular, Form, Policy, Certificate, Report
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)  # pdf, docx, xlsx
    uploaded_by: Mapped[str] = mapped_column(String(255), nullable=False)
    uploaded_date: Mapped[str] = mapped_column(String(20), nullable=False)
    size: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g. "2.4 MB"
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    access_roles: Mapped[str] = mapped_column(String(255), nullable=False, default="all")  # comma-separated roles
    academic_year: Mapped[str | None] = mapped_column(String(20), nullable=True)
    entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # student, teacher, course, etc.
    entity_id: Mapped[str | None] = mapped_column(String(50), nullable=True)  # ID of the related entity
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

