import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.competency import RoleCompetency, UserCompetency
from app.models.course import Course, CourseCompetency
from app.models.learning import Recommendation
from app.schemas.recommendation import RecommendationResponse

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)


@router.get("")
def get_recommendations(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Return fresh personalized recommendations."""

    if not current_user.job_role_id:
        raise HTTPException(
            status_code=400,
            detail="User does not have a job role assigned.",
        )

    from app.services.recommendation_engine import refresh_recommendations

    refresh_recommendations(db, current_user)

    recommendations = (
        db.query(Recommendation)
        .filter(
            Recommendation.user_id == current_user.id,
            Recommendation.status.in_(["pending", "accepted"]),
        )
        .all()
    )

    course_ids = [r.course_id for r in recommendations]
    course_ratings: dict[uuid.UUID, tuple[float, int]] = {}
    if course_ids:
        from app.models.course_review import CourseReview
        from sqlalchemy import func

        ratings_query = (
            db.query(
                CourseReview.course_id,
                func.avg(CourseReview.helpfulness_rating).label("avg_rating"),
                func.count(CourseReview.id).label("review_count"),
            )
            .filter(CourseReview.course_id.in_(course_ids))
            .group_by(CourseReview.course_id)
            .all()
        )
        course_ratings = {
            r.course_id: (float(r.avg_rating), int(r.review_count))
            for r in ratings_query
        }

    recommendations.sort(
        key=lambda recommendation: (
            -float(recommendation.priority_score),
            -course_ratings.get(recommendation.course_id, (0.0, 0))[0],
            -float(recommendation.gap_score),
        )
    )

    result = []

    for recommendation in recommendations:

        course = db.get(Course, recommendation.course_id)

        if not course:
            continue

        mapping = (
            db.query(CourseCompetency)
            .filter(
                CourseCompetency.course_id == course.id,
                CourseCompetency.competency_id == recommendation.competency_id,
            )
            .first()
        )

        user_competency = (
            db.query(UserCompetency)
            .filter(
                UserCompetency.user_id == current_user.id,
                UserCompetency.competency_id == recommendation.competency_id,
            )
            .first()
        )

        role_competency = (
            db.query(RoleCompetency)
            .filter(
                RoleCompetency.role_id == current_user.job_role_id,
                RoleCompetency.competency_id == recommendation.competency_id,
            )
            .first()
        )

        current_level = (
            user_competency.current_level
            if user_competency
            else 1
        )

        required_level = (
            role_competency.required_level
            if role_competency
            else current_level
        )

        avg_rating, review_count = course_ratings.get(course.id, (0.0, 0))

        result.append(
            {
                "recommendation_id": recommendation.id,
                "course_id": course.id,
                "course_title": course.title,
                "provider": course.provider,
                "course_url": course.url,
                "competency_id": recommendation.competency_id,
                "current_level": current_level,
                "required_level": required_level,
                "course_target_level": (
                    mapping.target_level
                    if mapping
                    else None
                ),
                "gap_score": float(recommendation.gap_score),
                "priority_score": float(recommendation.priority_score),
                "average_helpfulness": round(avg_rating, 1),
                "review_count": review_count,
                "status": recommendation.status,
                "reason": recommendation.reason,
            }
        )

    return {
        "total_recommendations": len(result),
        "recommendations": result,
    }


@router.post(
    "/{recommendation_id}/accept",
)
def accept_recommendation(
    recommendation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Accept a recommendation - marks it as 'accepted'."""
    recommendation = db.scalar(
        select(Recommendation).where(
            Recommendation.id == recommendation_id,
            Recommendation.user_id == current_user.id,
        )
    )

    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found",
        )

    if recommendation.status == "accepted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recommendation already accepted",
        )

    recommendation.status = "accepted"
    db.commit()
    db.refresh(recommendation)

    return {"message": "Recommendation accepted", "recommendation_id": str(recommendation_id)}


@router.post(
    "/{recommendation_id}/dismiss",
)
def dismiss_recommendation(
    recommendation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Dismiss a recommendation - marks it as 'dismissed'."""
    recommendation = db.scalar(
        select(Recommendation).where(
            Recommendation.id == recommendation_id,
            Recommendation.user_id == current_user.id,
        )
    )

    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found",
        )

    if recommendation.status == "dismissed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recommendation already dismissed",
        )

    recommendation.status = "dismissed"
    db.commit()
    db.refresh(recommendation)

    return {"message": "Recommendation dismissed", "recommendation_id": str(recommendation_id)}
