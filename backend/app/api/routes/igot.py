"""
iGOT Karmayogi integration routes.

All routes delegate to the igot_client adapter which transparently
switches between live API calls and database data based on environment config.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.adapters.igot_client import enroll_user, get_course, search_courses
from app.dependencies import get_current_user
from app.database import get_db

router = APIRouter(prefix="/igot", tags=["iGOT Karmayogi"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class EnrollRequest(BaseModel):
    igot_user_id: str
    course_id: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/courses")
def list_igot_courses(
    query: str = "",
    domain: str | None = None,
    limit: int = 20,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Search the iGOT Karmayogi course catalogue.

    Returns live results when IGOT_API_URL and IGOT_API_KEY are configured;
    falls back to the local database otherwise.
    """
    if limit < 1 or limit > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="limit must be between 1 and 50.",
        )
    return search_courses(db=db, query=query, domain=domain, limit=limit)


@router.get("/courses/{course_id}")
def get_igot_course(
    course_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Fetch metadata for a single iGOT course by its ID.
    """
    course = get_course(db=db, course_id=course_id)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course '{course_id}' not found.",
        )
    return course


@router.post("/enroll")
def enroll_in_igot_course(
    payload: EnrollRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Enroll the current user in an iGOT course.
    """
    try:
        result = enroll_user(
            db=db,
            igot_user_id=payload.igot_user_id,
            course_id=payload.course_id,
            platform_user_id=str(current_user.id),
        )
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"iGOT enrolment failed: {exc}",
        )
