import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.substitution import SubstitutionRequest
from app.models.user import User
from app.schemas.campus import SubstitutionCreate, SubstitutionResponse, SubstitutionUpdate
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/substitutions", tags=["Substitutions"])


@router.get("/", response_model=list[SubstitutionResponse])
async def list_substitutions(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    result = await db.execute(select(SubstitutionRequest).order_by(SubstitutionRequest.date.desc()))
    subs = result.scalars().all()
    response = []
    for s in subs:
        suggested = json.loads(s.suggested_teachers) if s.suggested_teachers else None
        response.append(
            SubstitutionResponse(
                id=s.id,
                date=s.date,
                time=s.time,
                course=s.course,
                original_teacher=s.original_teacher,
                reason=s.reason,
                status=s.status,
                assigned_teacher=s.assigned_teacher,
                suggested_teachers=suggested,
            )
        )
    return response


@router.post("/", response_model=SubstitutionResponse, status_code=201)
async def create_substitution(
    data: SubstitutionCreate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)
):
    sub = SubstitutionRequest(
        id=str(uuid.uuid4()),
        date=data.date,
        time=data.time,
        course=data.course,
        original_teacher=data.original_teacher,
        reason=data.reason,
        status="pending",
        suggested_teachers=json.dumps(data.suggested_teachers) if data.suggested_teachers else None,
    )
    db.add(sub)
    await db.flush()
    await db.refresh(sub)
    return SubstitutionResponse(
        id=sub.id,
        date=sub.date,
        time=sub.time,
        course=sub.course,
        original_teacher=sub.original_teacher,
        reason=sub.reason,
        status=sub.status,
        suggested_teachers=data.suggested_teachers,
    )


@router.put("/{sub_id}", response_model=SubstitutionResponse)
async def update_substitution(
    sub_id: str, data: SubstitutionUpdate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)
):
    result = await db.execute(select(SubstitutionRequest).where(SubstitutionRequest.id == sub_id))
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Substitution request not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(sub, field, value)
    await db.flush()
    await db.refresh(sub)

    suggested = json.loads(sub.suggested_teachers) if sub.suggested_teachers else None
    return SubstitutionResponse(
        id=sub.id,
        date=sub.date,
        time=sub.time,
        course=sub.course,
        original_teacher=sub.original_teacher,
        reason=sub.reason,
        status=sub.status,
        assigned_teacher=sub.assigned_teacher,
        suggested_teachers=suggested,
    )
