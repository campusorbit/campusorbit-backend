from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.marketplace import MarketplaceIntegration
from app.redis import get_cached, set_cached
from app.schemas.campus import MarketplaceResponse

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])


@router.get("/integrations", response_model=list[MarketplaceResponse])
async def list_integrations(db: AsyncSession = Depends(get_db)):
    cached = await get_cached("marketplace:integrations")
    if cached:
        return cached

    result = await db.execute(select(MarketplaceIntegration).order_by(MarketplaceIntegration.name))
    items = result.scalars().all()
    data = [MarketplaceResponse.model_validate(i).model_dump() for i in items]
    await set_cached("marketplace:integrations", data, ttl=600)
    return items
