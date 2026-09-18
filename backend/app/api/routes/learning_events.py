import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models.profile import LearningEvent, OfficialProfile
from app.schemas.profile import LearningEventResponse

router = APIRouter(
    prefix="/learning-events",
    tags=["Learning Events"],
)


@router.get("", response_model=list[LearningEventResponse])
def list_learning_events(
    user_id: uuid.UUID | None = Query(None),
    event_type: str = None,
    status: str = None,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Admin-only: List learning events with optional filters."""
    stmt = select(LearningEvent).order_by(desc(LearningEvent.created_at))

    if user_id:
        stmt = stmt.where(LearningEvent.profile_id == user_id)
    if event_type:
        stmt = stmt.where(LearningEvent.event_type == event_type)
    if status:
        stmt = stmt.where(LearningEvent.status == status)

    stmt = stmt.limit(limit)
    events = db.scalars(stmt).all()

    return [
        LearningEventResponse(
            id=e.id,
            profile_id=e.profile_id,
            course_id=e.course_id,
            event_type=e.event_type,
            status=e.status,
            score=float(e.score) if e.score is not None else None,
            external_id=e.external_id,
            created_at=e.created_at,
        )
        for e in events
    ]
