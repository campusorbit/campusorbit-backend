import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.vendor import Vendor
from app.models.user import User
from app.schemas.erp_modules import VendorCreate, VendorResponse
from app.services.auth_service import require_roles

router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.get("/", response_model=list[VendorResponse])
async def list_vendors(
    category: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    query = select(Vendor).order_by(Vendor.name)
    if category:
        query = query.where(Vendor.category == category)
    if status:
        query = query.where(Vendor.status == status)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=VendorResponse, status_code=201)
async def create_vendor(
    data: VendorCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    vendor = Vendor(id=str(uuid.uuid4()), status="active", **data.model_dump())
    db.add(vendor)
    await db.flush()
    await db.refresh(vendor)
    return vendor
