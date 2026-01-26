from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.transport import TransportBus
from app.models.user import User
from app.redis import get_cached, set_cached
from app.schemas.campus import TransportBusResponse, TransportBusUpdate
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/transport", tags=["Transport"])


@router.get("/buses", response_model=list[TransportBusResponse])
async def list_buses(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    cached = await get_cached("transport:buses")
    if cached:
        return cached

    result = await db.execute(select(TransportBus))
    buses = result.scalars().all()
    data = [TransportBusResponse.model_validate(b).model_dump() for b in buses]
    await set_cached("transport:buses", data, ttl=30)
    return buses


@router.put("/buses/{bus_id}", response_model=TransportBusResponse)
async def update_bus_location(
    bus_id: str, data: TransportBusUpdate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)
):
    result = await db.execute(select(TransportBus).where(TransportBus.id == bus_id))
    bus = result.scalar_one_or_none()
    if not bus:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bus not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(bus, field, value)
    await db.flush()
    await db.refresh(bus)
    return bus
