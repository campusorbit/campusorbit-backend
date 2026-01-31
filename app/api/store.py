import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.store import StoreOrder, StoreProduct
from app.models.user import User
from app.schemas.erp_modules import StoreOrderCreate, StoreOrderResponse, StoreProductResponse
from app.services.auth_service import get_current_user, require_roles

router = APIRouter(prefix="/store", tags=["Online Store"])


@router.get("/products", response_model=list[StoreProductResponse])
async def list_products(
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(StoreProduct).where(StoreProduct.is_active == True).order_by(StoreProduct.name)  # noqa: E712
    if category:
        query = query.where(StoreProduct.category == category)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/orders", response_model=list[StoreOrderResponse])
async def list_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(StoreOrder).order_by(StoreOrder.order_date.desc())
    # Students/parents see only their orders; admin/employee see all
    if current_user.role.value in ("student", "parent"):
        query = query.where(StoreOrder.student_id == current_user.id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/orders", response_model=StoreOrderResponse, status_code=201)
async def create_order(
    data: StoreOrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify product exists and has stock
    prod_result = await db.execute(select(StoreProduct).where(StoreProduct.id == data.product_id))
    product = prod_result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock < data.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    from datetime import datetime
    order = StoreOrder(
        id=str(uuid.uuid4()),
        student_id=current_user.id,
        student_name=current_user.name,
        product_id=product.id,
        product_name=product.name,
        quantity=data.quantity,
        unit_price=product.price,
        total=product.price * data.quantity,
        status="pending",
        order_date=datetime.now().strftime("%Y-%m-%d"),
    )
    product.stock -= data.quantity
    db.add(order)
    await db.flush()
    await db.refresh(order)
    return order
