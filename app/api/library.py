import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.library import LibraryBook, BookIssue
from app.models.user import User
from app.schemas.erp_modules import BookIssueCreate, BookIssueResponse, LibraryBookResponse
from app.services.auth_service import get_current_user, require_roles

router = APIRouter(prefix="/library", tags=["Library"])


@router.get("/books", response_model=list[LibraryBookResponse])
async def list_books(
    category: str | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(LibraryBook).order_by(LibraryBook.title)
    if category:
        query = query.where(LibraryBook.category == category)
    if search:
        query = query.where(LibraryBook.title.ilike(f"%{search}%"))
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/issues", response_model=list[BookIssueResponse])
async def list_issues(
    student_id: str | None = None,
    status_filter: str | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(BookIssue).order_by(BookIssue.issue_date.desc())
    if student_id:
        query = query.where(BookIssue.student_id == student_id)
    if status_filter:
        query = query.where(BookIssue.status == status_filter)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/issues", response_model=BookIssueResponse, status_code=201)
async def issue_book(
    data: BookIssueCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles("admin", "teacher", "employee")),
):
    # Check book availability
    book_result = await db.execute(select(LibraryBook).where(LibraryBook.id == data.book_id))
    book = book_result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.available_copies <= 0:
        raise HTTPException(status_code=400, detail="No copies available")

    issue = BookIssue(id=str(uuid.uuid4()), status="issued", **data.model_dump())
    book.available_copies -= 1
    db.add(issue)
    await db.flush()
    await db.refresh(issue)
    return issue


@router.put("/issues/{issue_id}/return", response_model=BookIssueResponse)
async def return_book(
    issue_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles("admin", "teacher", "employee")),
):
    result = await db.execute(select(BookIssue).where(BookIssue.id == issue_id))
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue record not found")

    issue.status = "returned"
    issue.return_date = "2025-01-15"  # In production: datetime.now().strftime("%Y-%m-%d")

    # Increment available copies
    book_result = await db.execute(select(LibraryBook).where(LibraryBook.id == issue.book_id))
    book = book_result.scalar_one_or_none()
    if book:
        book.available_copies += 1

    await db.flush()
    await db.refresh(issue)
    return issue
