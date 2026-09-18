import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models.course import Course, CourseCompetency
from app.models.course_review import CourseReview
from app.models.learning import Progress
from app.models.user import User
from app.schemas.course import CourseResponse, CourseCreateRequest, CourseUpdateRequest
from app.schemas.course_review import (
    CourseReviewCreate,
    CourseReviewResponse,
    CourseReviewStats,
)

router = APIRouter(
    prefix="/courses",
    tags=["Courses"],
)


@router.get(
    "",
    response_model=list[CourseResponse],
)
def get_courses(
    db: Session = Depends(get_db),
):
    statement = (
        select(Course)
        .where(Course.is_active.is_(True))
        .order_by(Course.title)
    )

    return db.scalars(statement).all()


@router.post(
    "",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_course(
    data: CourseCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Admin-only: Create a new course."""
    course = Course(
        title=data.title,
        description=data.description,
        provider=data.provider,
        source=data.source,
        external_id=data.external_id,
        url=data.url,
        duration_minutes=data.duration_minutes,
        level=data.level,
        is_active=True,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.put(
    "/{course_id}",
    response_model=CourseResponse,
)
def update_course(
    course_id: uuid.UUID,
    data: CourseUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Admin-only: Update an existing course."""
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    if data.title is not None:
        course.title = data.title
    if data.description is not None:
        course.description = data.description
    if data.provider is not None:
        course.provider = data.provider
    if data.source is not None:
        course.source = data.source
    if data.external_id is not None:
        course.external_id = data.external_id
    if data.url is not None:
        course.url = data.url
    if data.duration_minutes is not None:
        course.duration_minutes = data.duration_minutes
    if data.level is not None:
        course.level = data.level

    db.commit()
    db.refresh(course)
    return course


@router.delete(
    "/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_course(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Admin-only: Deactivate (soft delete) a course."""
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    course.is_active = False
    db.commit()


@router.post(
    "/{course_id}/reviews",
    response_model=CourseReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_or_update_course_review(
    course_id: uuid.UUID,
    review_in: CourseReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit or update a course helpfulness review.
    Only employees who have completed the course can submit a review.
    """
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    # Check if user has completed the course
    progress = db.scalar(
        select(Progress).where(
            Progress.user_id == current_user.id,
            Progress.course_id == course_id,
            Progress.status == "completed",
        )
    )
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only review courses you have completed.",
        )

    # Check for existing review (upsert)
    review = db.scalar(
        select(CourseReview).where(
            CourseReview.user_id == current_user.id,
            CourseReview.course_id == course_id,
        )
    )

    if review:
        review.helpfulness_rating = review_in.helpfulness_rating
        review.comments = review_in.comments
    else:
        review = CourseReview(
            user_id=current_user.id,
            course_id=course_id,
            helpfulness_rating=review_in.helpfulness_rating,
            comments=review_in.comments,
        )
        db.add(review)

    db.commit()
    db.refresh(review)

    return CourseReviewResponse(
        id=review.id,
        user_id=review.user_id,
        user_name=current_user.full_name,
        course_id=review.course_id,
        helpfulness_rating=review.helpfulness_rating,
        comments=review.comments,
        created_at=review.created_at,
    )


@router.get(
    "/{course_id}/reviews",
    response_model=list[CourseReviewResponse],
)
def get_course_reviews(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Get all reviews for a specific course."""
    reviews = (
        db.scalars(
            select(CourseReview)
            .where(CourseReview.course_id == course_id)
            .order_by(CourseReview.created_at.desc())
        )
        .all()
    )

    return [
        CourseReviewResponse(
            id=r.id,
            user_id=r.user_id,
            user_name=r.user.full_name if r.user else "Anonymous",
            course_id=r.course_id,
            helpfulness_rating=r.helpfulness_rating,
            comments=r.comments,
            created_at=r.created_at,
        )
        for r in reviews
    ]


@router.get(
    "/{course_id}/reviews/stats",
    response_model=CourseReviewStats,
)
def get_course_review_stats(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Get aggregate helpfulness stats for a course."""
    stats = db.execute(
        select(
            func.avg(CourseReview.helpfulness_rating).label("avg_rating"),
            func.count(CourseReview.id).label("total_reviews"),
        ).where(CourseReview.course_id == course_id)
    ).first()

    avg_rating = float(stats.avg_rating) if stats and stats.avg_rating else 0.0
    total = int(stats.total_reviews) if stats and stats.total_reviews else 0

    recent_reviews = (
        db.scalars(
            select(CourseReview)
            .where(CourseReview.course_id == course_id)
            .order_by(CourseReview.created_at.desc())
            .limit(5)
        )
        .all()
    )

    return CourseReviewStats(
        course_id=course_id,
        average_helpfulness=round(avg_rating, 1),
        total_reviews=total,
        reviews=[
            CourseReviewResponse(
                id=r.id,
                user_id=r.user_id,
                user_name=r.user.full_name if r.user else "Anonymous",
                course_id=r.course_id,
                helpfulness_rating=r.helpfulness_rating,
                comments=r.comments,
                created_at=r.created_at,
            )
            for r in recent_reviews
        ],
    )
