import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.campus import CampusNews
from app.models.user import User
from app.redis import get_cached, invalidate_cache, set_cached
from app.schemas.campus import CampusNewsCreate, CampusNewsResponse
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/campus", tags=["Campus"])


@router.get("/news", response_model=list[CampusNewsResponse])
async def list_news(db: AsyncSession = Depends(get_db)):
    cached = await get_cached("campus:news")
    if cached:
        return cached

    result = await db.execute(select(CampusNews).order_by(CampusNews.date.desc()).limit(50))
    news = result.scalars().all()
    data = [CampusNewsResponse.model_validate(n).model_dump() for n in news]
    await set_cached("campus:news", data, ttl=120)
    return news


@router.post("/news", response_model=CampusNewsResponse, status_code=201)
async def create_news(
    data: CampusNewsCreate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)
):
    news = CampusNews(id=str(uuid.uuid4()), **data.model_dump())
    db.add(news)
    await db.flush()
    await db.refresh(news)
    await invalidate_cache("campus:*")
    return news


@router.get("/directory", response_model=list)
async def campus_directory(
    role: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    from app.schemas.user import UserResponse

    query = select(User).where(User.is_active.is_(True))
    if role:
        query = query.where(User.role == role)
    result = await db.execute(query.order_by(User.name).limit(200))
    return result.scalars().all()
