import json

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.pricing import PricingPlan
from app.redis import get_cached, set_cached
from app.schemas.campus import PricingPlanResponse

router = APIRouter(prefix="/pricing", tags=["Pricing"])


@router.get("/plans", response_model=list[PricingPlanResponse])
async def list_pricing_plans(db: AsyncSession = Depends(get_db)):
    cached = await get_cached("pricing:plans")
    if cached:
        return cached

    result = await db.execute(select(PricingPlan).order_by(PricingPlan.price))
    plans = result.scalars().all()

    response = []
    for plan in plans:
        features = json.loads(plan.features) if isinstance(plan.features, str) else plan.features
        response.append(
            PricingPlanResponse(
                id=plan.id,
                name=plan.name,
                price=plan.price,
                features=features,
                icon=plan.icon,
                highlighted=plan.highlighted,
            )
        )

    await set_cached("pricing:plans", [r.model_dump() for r in response], ttl=600)
    return response
