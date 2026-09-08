from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.competency import (
    RoleCompetency,
    UserCompetency,
)
from app.models.course import Course, CourseCompetency
from app.models.learning import Recommendation


router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("")
def get_recommendations(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Generate personalized course recommendations based on:

    1. User's competency gaps
    2. Required competency level for the user's role
    3. Competency priority
    4. Course target level
    """

    if not current_user.job_role_id:
        raise HTTPException(
            status_code=400,
            detail="User does not have a job role assigned.",
        )

    # ---------------------------------------------------------
    # 1. Get role competency requirements
    # ---------------------------------------------------------
    role_competencies = (
        db.query(RoleCompetency)
        .filter(RoleCompetency.role_id == current_user.job_role_id)
        .all()
    )

    if not role_competencies:
        return {
            "total_recommendations": 0,
            "recommendations": [],
        }

    # ---------------------------------------------------------
    # 2. Get user's current competency levels
    # ---------------------------------------------------------
    user_competencies = (
        db.query(UserCompetency)
        .filter(UserCompetency.user_id == current_user.id)
        .all()
    )

    current_levels = {
        uc.competency_id: uc.current_level
        for uc in user_competencies
    }

    recommendations = []

    # ---------------------------------------------------------
    # 3. Process every competency gap
    # ---------------------------------------------------------
    for role_competency in role_competencies:

        current_level = current_levels.get(
            role_competency.competency_id,
            1,
        )

        required_level = role_competency.required_level

        gap = max(required_level - current_level, 0)

        # No gap => no learning recommendation required
        if gap == 0:
            continue

        # Competency priority
        criticality_weight = 2 if role_competency.is_critical else 0

        priority_score = (
            (gap * 2)
            + criticality_weight
            + role_competency.organizational_priority
        )

        # -----------------------------------------------------
        # 4. Find courses mapped to this competency
        # -----------------------------------------------------
        course_mappings = (
            db.query(CourseCompetency)
            .filter(
        CourseCompetency.competency_id
        == role_competency.competency_id,
        CourseCompetency.target_level > current_level,
)
         .all()
        )

        if not course_mappings:
            continue

        # -----------------------------------------------------
        # 5. Prefer courses that can actually reach the
        #    required level
        # -----------------------------------------------------
        reaching_required = [
            mapping
            for mapping in course_mappings
            if mapping.target_level >= required_level
        ]

        if reaching_required:
            eligible_courses = reaching_required
        else:
            # No course reaches the required level.
            # Use the highest available stepping-stone level.
            highest_target = max(
                mapping.target_level
                for mapping in course_mappings
            )

            eligible_courses = [
                mapping
                for mapping in course_mappings
                if mapping.target_level == highest_target
            ]

        # -----------------------------------------------------
        # 6. Rank courses for this competency
        # -----------------------------------------------------
        eligible_courses.sort(
            key=lambda mapping: (
                abs(mapping.target_level - required_level),
                -mapping.target_level,
            )
        )

        # -----------------------------------------------------
        # 7. Create recommendation records
        # -----------------------------------------------------
        for mapping in eligible_courses:

            course = db.get(Course, mapping.course_id)

            if not course:
                continue

            recommendation = (
                db.query(Recommendation)
                .filter(
                    Recommendation.user_id == current_user.id,
                    Recommendation.course_id == course.id,
                    Recommendation.competency_id
                    == role_competency.competency_id,
                )
                .first()
            )

            reason = (
                f"Current level: {current_level}, "
                f"Required level: {required_level}, "
                f"Gap: {gap}, "
                f"Course target level: {mapping.target_level}."
            )

            if recommendation:
                recommendation.gap_score = gap
                recommendation.priority_score = priority_score
                recommendation.reason = reason
                recommendation.status = "pending"
            else:
                recommendation = Recommendation(
                    user_id=current_user.id,
                    course_id=course.id,
                    competency_id=role_competency.competency_id,
                    gap_score=gap,
                    priority_score=priority_score,
                    reason=reason,
                    status="pending",
                )

                db.add(recommendation)

            recommendations.append(
                {
                    "recommendation_id": recommendation.id,
                    "course_id": course.id,
                    "course_title": course.title,
                    "provider": course.provider,
                    "competency_id": role_competency.competency_id,
                    "current_level": current_level,
                    "required_level": required_level,
                    "course_target_level": mapping.target_level,
                    "gap_score": gap,
                    "priority_score": priority_score,
                    "is_critical": role_competency.is_critical,
                    "organizational_priority": (
                        role_competency.organizational_priority
                    ),
                    "reason": reason,
                }
            )

    db.commit()

    # ---------------------------------------------------------
    # 8. Global ranking
    #
    # Higher competency priority first.
    # Within the same priority, prefer the course whose target
    # level is closest to the required level.
    # ---------------------------------------------------------
    recommendations.sort(
        key=lambda item: (
            -item["priority_score"],
            abs(
                item["course_target_level"]
                - item["required_level"]
            ),
            -item["course_target_level"],
            item["course_title"],
        )
    )

    return {
        "total_recommendations": len(recommendations),
        "recommendations": recommendations,
    }