import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.erp_modules import DocumentCreate, DocumentResponse
from app.services.auth_service import get_current_user, require_roles

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/", response_model=list[DocumentResponse])
async def list_documents(
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Document).order_by(Document.uploaded_date.desc())
    if category:
        query = query.where(Document.category == category)
    result = await db.execute(query)
    docs = result.scalars().all()
    # Filter by role access
    user_role = current_user.role.value
    return [d for d in docs if d.access_roles == "all" or user_role in d.access_roles.split(",")]


@router.post("/", response_model=DocumentResponse, status_code=201)
async def create_document(
    data: DocumentCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles("admin", "teacher")),
):
    doc = Document(id=str(uuid.uuid4()), **data.model_dump())
    db.add(doc)
    await db.flush()
    await db.refresh(doc)
    return doc
