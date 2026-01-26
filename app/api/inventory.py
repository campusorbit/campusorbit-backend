import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.inventory import InventoryItem
from app.models.user import User
from app.schemas.campus import InventoryCreate, InventoryResponse
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("/", response_model=list[InventoryResponse])
async def list_inventory(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    result = await db.execute(select(InventoryItem).order_by(InventoryItem.name))
    return result.scalars().all()


@router.post("/", response_model=InventoryResponse, status_code=201)
async def create_inventory_item(
    data: InventoryCreate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)
):
    item = InventoryItem(id=str(uuid.uuid4()), **data.model_dump())
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


@router.put("/{item_id}", response_model=InventoryResponse)
async def update_inventory_item(
    item_id: str, data: InventoryCreate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)
):
    result = await db.execute(select(InventoryItem).where(InventoryItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    for field, value in data.model_dump().items():
        setattr(item, field, value)
    await db.flush()
    await db.refresh(item)
    return item
