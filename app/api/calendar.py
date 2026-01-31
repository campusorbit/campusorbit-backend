import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.calendar_event import CalendarEvent
from app.models.user import User
from app.schemas.erp_modules import CalendarEventCreate, CalendarEventResponse
from app.services.auth_service import get_current_user, require_roles

router = APIRouter(prefix="/calendar", tags=["Calendar & Events"])


@router.get("/events", response_model=list[CalendarEventResponse])
async def list_events(
    event_type: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(CalendarEvent).order_by(CalendarEvent.start_date.desc())
    if event_type:
        query = query.where(CalendarEvent.event_type == event_type)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/events", response_model=CalendarEventResponse, status_code=201)
async def create_event(
    data: CalendarEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher")),
):
    event = CalendarEvent(
        id=str(uuid.uuid4()),
        created_by=current_user.name,
        **data.model_dump(),
    )
    db.add(event)
    await db.flush()
    await db.refresh(event)
    return event
