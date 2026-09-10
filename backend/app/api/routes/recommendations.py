from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.competency import (
    RoleCompetency,
    UserCompetency,
)
from app.models.course import (
    Course,
    CourseCompetency,
)
from app.models.learning import Recommendation
from app.services.recommendation_engine import (
    refresh_recommendations,
)


router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"],
)


@router.get("")
def get_recommendations(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Return fresh personalized recommendations.

    Phase 5:
    Recommendations are recalculated whenever this endpoint
    is called so they always reflect the latest competency gaps.
    """

    if not current_user.job_role_id:
        raise HTTPException(
            status_code=400,
            detail=(
                "User does not have a job role assigned."
            ),
        )

    refresh_recommendations(
        db,
        current_user,
    )

    recommendations = (
        db.query(Recommendation)
        .filter(
            Recommendation.user_id
            == current_user.id,
            Recommendation.status.in_(
                ["pending", "accepted"]
            ),
        )
        .all()
    )

    recommendations.sort(
        key=lambda recommendation: (
            -float(
                recommendation.priority_score
            ),
            -float(
                recommendation.gap_score
            ),
        )
    )

    result = []

    for recommendation in recommendations:

        course = db.get(
            Course,
            recommendation.course_id,
        )

        if not course:
            continue

        mapping = (
            db.query(CourseCompetency)
            .filter(
                CourseCompetency.course_id
                == course.id,
                CourseCompetency.competency_id
                == recommendation.competency_id,
            )
            .first()
        )

        user_competency = (
            db.query(UserCompetency)
            .filter(
                UserCompetency.user_id
                == current_user.id,
                UserCompetency.competency_id
                == recommendation.competency_id,
            )
            .first()
        )

        role_competency = (
            db.query(RoleCompetency)
            .filter(
                RoleCompetency.role_id
                == current_user.job_role_id,
                RoleCompetency.competency_id
                == recommendation.competency_id,
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

        result.append(
            {
                "recommendation_id": recommendation.id,
                "course_id": course.id,
                "course_title": course.title,
                "provider": course.provider,
                "course_url": course.url,
                "competency_id": (
                    recommendation.competency_id
                ),
                "current_level": current_level,
                "required_level": required_level,
                "course_target_level": (
                    mapping.target_level
                    if mapping
                    else None
                ),
                "gap_score": float(
                    recommendation.gap_score
                ),
                "priority_score": float(
                    recommendation.priority_score
                ),
                "status": recommendation.status,
                "reason": recommendation.reason,
            }
        )

    return {
        "total_recommendations": len(result),
        "recommendations": result,
    }