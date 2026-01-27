from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.attendance import Attendance
from app.models.course import Course
from app.models.fee import Fee
from app.models.lead import Lead
from app.models.notification import Notification
from app.models.user import User
from app.redis import get_cached, set_cached
from app.schemas.campus import NotificationResponse
from app.schemas.dashboard import DashboardStats
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cache_key = f"dashboard:stats:{current_user.role.value}"
    cached = await get_cached(cache_key)
    if cached:
        return cached

    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
    active_courses = (await db.execute(select(func.count(Course.id)))).scalar() or 0

    # Attendance percentage
    total_att = (await db.execute(select(func.count(Attendance.id)))).scalar() or 0
    present_att = (await db.execute(select(func.count(Attendance.id)).where(Attendance.status == "present"))).scalar() or 0
    avg_attendance = (present_att / total_att * 100) if total_att > 0 else 0

    # Financial
    paid_sum = (await db.execute(select(func.coalesce(func.sum(Fee.amount), 0)).where(Fee.status == "paid"))).scalar() or 0
    pending_sum = (await db.execute(select(func.coalesce(func.sum(Fee.amount), 0)).where(Fee.status == "pending"))).scalar() or 0
    overdue_sum = (await db.execute(select(func.coalesce(func.sum(Fee.amount), 0)).where(Fee.status == "overdue"))).scalar() or 0
    total_fees = paid_sum + pending_sum + overdue_sum
    collection_rate = (paid_sum / total_fees * 100) if total_fees > 0 else 0

    online_sum = (await db.execute(select(func.coalesce(func.sum(Fee.amount), 0)).where(Fee.payment_mode == "online", Fee.status == "paid"))).scalar() or 0
    online_pct = (online_sum / paid_sum * 100) if paid_sum > 0 else 0

    new_leads = (await db.execute(select(func.count(Lead.id)))).scalar() or 0

    stats = DashboardStats(
        total_users=total_users,
        active_courses=active_courses,
        avg_attendance=round(avg_attendance, 1),
        pending_tasks=7,
        total_collected=paid_sum,
        total_pending=pending_sum,
        collection_rate=round(collection_rate, 1),
        online_percentage=round(online_pct, 1),
        new_leads=new_leads,
    )

    await set_cached(cache_key, stats.model_dump(), ttl=60)
    return stats


@router.get("/notifications", response_model=list[NotificationResponse])
async def get_my_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(20)
    )
    return result.scalars().all()
