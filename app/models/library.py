from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LibraryBook(Base):
    __tablename__ = "library_books"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    isbn: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # Fiction, Science, Engineering, etc.
    total_copies: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    available_copies: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    shelf_location: Mapped[str] = mapped_column(String(50), nullable=False)
    publisher: Mapped[str | None] = mapped_column(String(255), nullable=True)
    published_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    barcode: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    issues: Mapped[list["BookIssue"]] = relationship(back_populates="book")


class BookIssue(Base):
    __tablename__ = "book_issues"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    book_id: Mapped[str] = mapped_column(String(50), ForeignKey("library_books.id"), nullable=False)
    student_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), nullable=False)
    issue_date: Mapped[str] = mapped_column(String(20), nullable=False)
    due_date: Mapped[str] = mapped_column(String(20), nullable=False)
    return_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="issued")  # issued, returned, overdue
    fine: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    book: Mapped["LibraryBook"] = relationship(back_populates="issues")
