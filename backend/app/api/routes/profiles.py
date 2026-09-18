import uuid
from typing import Optional
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin, get_current_user
from app.models.user import User
from app.models.profile import OfficialProfile, LearningEvent
from app.models.course import Course
from app.schemas.profile import OfficialProfileResponse

router = APIRouter(
    prefix="/profiles",
    tags=["Official Profiles"],
)


@router.get("/me", response_model=OfficialProfileResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current user's official profile."""
    profile = db.scalar(
        select(OfficialProfile).where(OfficialProfile.user_id == current_user.id)
    )
    if not profile:
        profile = OfficialProfile(user_id=current_user.id, data_source="manual")
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.put("/me", response_model=OfficialProfileResponse)
def update_my_profile(
    designation: Optional[str] = None,
    department: Optional[str] = None,
    cadre: Optional[str] = None,
    education: Optional[str] = None,
    experience_years: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the current user's official profile."""
    profile = db.scalar(
        select(OfficialProfile).where(OfficialProfile.user_id == current_user.id)
    )
    if not profile:
        profile = OfficialProfile(user_id=current_user.id, data_source="manual")
        db.add(profile)

    if designation is not None:
        profile.designation = designation
    if department is not None:
        profile.department = department
    if cadre is not None:
        profile.cadre = cadre
    if education is not None:
        profile.education = education
    if experience_years is not None:
        profile.experience_years = experience_years

    profile.updated_at = db.execute(
        select(func.now())
    ).scalar() if False else None

    from datetime import datetime, timezone
    profile.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(profile)
    return profile


@router.get("/{user_id}", response_model=OfficialProfileResponse)
def get_profile(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Admin-only: Get official profile by user ID."""
    profile = db.get(OfficialProfile, user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@router.post("/{user_id}/events", status_code=status.HTTP_201_CREATED)
def record_learning_event(
    user_id: uuid.UUID,
    course_id: uuid.UUID,
    event_type: str,
    status: str = "completed",
    score: Optional[float] = None,
    external_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Admin-only: Record a learning event (enrolment, completion, score)."""
    if event_type not in ("enrolment", "completion", "score", "progress"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid event type")
    if status not in ("pending", "in_progress", "completed", "failed"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")

    profile = db.scalar(
        select(OfficialProfile).where(OfficialProfile.user_id == user_id)
    )
    if not profile:
        profile = OfficialProfile(user_id=user_id, data_source="manual")
        db.add(profile)
        db.flush()

    event = LearningEvent(
        profile_id=profile.id,
        course_id=course_id,
        event_type=event_type,
        status=status,
        score=score,
        external_id=external_id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return {"message": "Learning event recorded", "event_id": str(event.id)}


@router.get("/{user_id}/assessments")
def get_profile_assessments(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Admin-only: Get all competency assessment records for a user."""
    from app.models.profile import CompetencyAssessmentRecord
    from app.models.competency import Competency

    profile = db.scalar(
        select(OfficialProfile).where(OfficialProfile.user_id == user_id)
    )
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    records = db.query(CompetencyAssessmentRecord, Competency).join(
        Competency, CompetencyAssessmentRecord.competency_id == Competency.id
    ).filter(CompetencyAssessmentRecord.profile_id == profile.id).all()

    return [
        {
            "id": str(r.id),
            "competency_id": str(r.competency_id),
            "competency_name": c.name,
            "domain": c.domain,
            "proficiency_score": r.proficiency_score,
            "proficiency_level": r.proficiency_level,
            "source": r.source,
            "confidence": r.confidence,
            "assessed_at": r.assessed_at,
        }
        for r, c in records
    ]


@router.post("/{user_id}/complete-course")
def complete_course(
    user_id: uuid.UUID,
    course_id: uuid.UUID,
    score: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Record course completion and trigger gap recalculation."""
    from app.services.event_bus import publish_course_completion, event_bus
    from app.services.recommendation_engine import refresh_recommendations

    profile = db.scalar(
        select(OfficialProfile).where(OfficialProfile.user_id == user_id)
    )
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    event = LearningEvent(
        profile_id=profile.id,
        course_id=course_id,
        event_type="completion",
        status="completed",
        score=score,
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    if score is not None:
        publish_course_completion(user_id, str(course_id), score)

    user = db.get(User, user_id)
    if user and user.job_role_id:
        refresh_recommendations(db, user)

    return {"message": "Course completion recorded", "event_id": str(event.id)}
