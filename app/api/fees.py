import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.fee import Fee
from app.models.user import User
from app.redis import get_cached, set_cached
from app.schemas.fee import FeeChartData, FeeCreate, FeeResponse, FinancialKPIs, PaymentGatewayStatus
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/fees", tags=["Fees"])


@router.get("/", response_model=list[FeeResponse])
async def list_fees(
    student_id: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(Fee)
    if student_id:
        query = query.where(Fee.student_id == student_id)
    if status_filter:
        query = query.where(Fee.status == status_filter)
    result = await db.execute(query.order_by(Fee.due_date.desc()).limit(100))
    return result.scalars().all()


@router.post("/", response_model=FeeResponse, status_code=201)
async def create_fee(data: FeeCreate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    fee = Fee(id=str(uuid.uuid4()), **data.model_dump())
    db.add(fee)
    await db.flush()
    await db.refresh(fee)
    return fee


@router.get("/kpis", response_model=FinancialKPIs)
async def get_financial_kpis(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    cached = await get_cached("fees:kpis")
    if cached:
        return cached

    paid = (await db.execute(select(func.coalesce(func.sum(Fee.amount), 0)).where(Fee.status == "paid"))).scalar() or 0
    pending = (await db.execute(select(func.coalesce(func.sum(Fee.amount), 0)).where(Fee.status == "pending"))).scalar() or 0
    overdue = (await db.execute(select(func.coalesce(func.sum(Fee.amount), 0)).where(Fee.status == "overdue"))).scalar() or 0
    total = paid + pending + overdue
    collection_rate = (paid / total * 100) if total > 0 else 0

    online = (await db.execute(select(func.coalesce(func.sum(Fee.amount), 0)).where(Fee.payment_mode == "online", Fee.status == "paid"))).scalar() or 0
    offline = paid - online

    student_count = (await db.execute(select(func.count(func.distinct(Fee.student_id))))).scalar() or 1
    avg_fee = paid // max(student_count, 1)

    kpis = FinancialKPIs(
        total_collected=paid,
        total_pending=pending,
        total_overdue=overdue,
        collection_rate=round(collection_rate, 1),
        online_payments=online,
        offline_payments=offline,
        average_fee_per_student=avg_fee,
    )

    await set_cached("fees:kpis", kpis.model_dump(), ttl=60)
    return kpis


@router.get("/chart-data", response_model=list[FeeChartData])
async def get_fee_chart_data(_: User = Depends(get_current_user)):
    cached = await get_cached("fees:chart")
    if cached:
        return cached

    # Return seed chart data structure
    data = [
        FeeChartData(month="Jan", online=2400, offline=1200, pending=800),
        FeeChartData(month="Feb", online=2800, offline=1400, pending=600),
        FeeChartData(month="Mar", online=3200, offline=1100, pending=900),
        FeeChartData(month="Apr", online=3500, offline=1500, pending=500),
        FeeChartData(month="May", online=4200, offline=1800, pending=400),
        FeeChartData(month="Jun", online=4800, offline=2000, pending=300),
    ]

    await set_cached("fees:chart", [d.model_dump() for d in data], ttl=300)
    return data


@router.get("/gateways", response_model=list[PaymentGatewayStatus])
async def get_payment_gateways(_: User = Depends(get_current_user)):
    cached = await get_cached("fees:gateways")
    if cached:
        return cached

    gateways = [
        PaymentGatewayStatus(name="Razorpay", status="active", success_rate=99.2, transactions=1250),
        PaymentGatewayStatus(name="PayU", status="active", success_rate=98.8, transactions=980),
        PaymentGatewayStatus(name="Offline Bank Transfer", status="active", success_rate=100, transactions=320),
    ]

    await set_cached("fees:gateways", [g.model_dump() for g in gateways], ttl=300)
    return gateways
