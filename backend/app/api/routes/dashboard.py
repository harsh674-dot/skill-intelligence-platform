from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.competency import (
    Competency,
    RoleCompetency,
    UserCompetency,
)
from app.models.course import Course, CourseCompetency
from app.models.role import Role


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


PROFICIENCY_LABELS = {
    1: "Beginner",
    2: "Basic",
    3: "Intermediate",
    4: "Advanced",
    5: "Expert",
}


@router.get("")
def get_employee_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # ---------------------------------------------------------
    # 1. Validate employee role
    # ---------------------------------------------------------
    if not current_user.job_role_id:
        raise HTTPException(
            status_code=400,
            detail="User does not have a job role assigned.",
        )

    role = db.get(Role, current_user.job_role_id)

    if not role:
        raise HTTPException(
            status_code=404,
            detail="Assigned role not found.",
        )

    # ---------------------------------------------------------
    # 2. Get role competency requirements
    # ---------------------------------------------------------
    role_competencies = (
        db.query(RoleCompetency)
        .filter(
            RoleCompetency.role_id == current_user.job_role_id
        )
        .all()
    )

    # ---------------------------------------------------------
    # 3. Get employee's current competency levels
    # ---------------------------------------------------------
    user_competencies = (
        db.query(UserCompetency)
        .filter(
            UserCompetency.user_id == current_user.id
        )
        .all()
    )

    current_levels = {
        uc.competency_id: uc.current_level
        for uc in user_competencies
    }

    # ---------------------------------------------------------
    # 4. Build competency dashboard
    # ---------------------------------------------------------
    competencies = []
    priority_gaps = []

    for role_competency in role_competencies:

        competency = db.get(
            Competency,
            role_competency.competency_id,
        )

        if not competency:
            continue

        current_level = current_levels.get(
            role_competency.competency_id,
            1,
        )

        required_level = role_competency.required_level

        gap = max(
            required_level - current_level,
            0,
        )

        criticality_weight = (
            2 if role_competency.is_critical else 0
        )

        priority_score = (
            (gap * 2)
            + criticality_weight
            + role_competency.organizational_priority
        )

        competency_data = {
            "competency_id": competency.id,
            "competency_name": competency.name,
            "domain": competency.domain,
            "current_level": current_level,
            "current_level_label": PROFICIENCY_LABELS.get(
                current_level,
                "Unknown",
            ),
            "required_level": required_level,
            "required_level_label": PROFICIENCY_LABELS.get(
                required_level,
                "Unknown",
            ),
            "gap": gap,
            "is_critical": role_competency.is_critical,
            "organizational_priority": (
                role_competency.organizational_priority
            ),
            "priority_score": priority_score,
        }

        competencies.append(competency_data)

        if gap > 0:
            priority_gaps.append(competency_data)

    # Highest priority gaps first
    priority_gaps.sort(
        key=lambda item: (
            -item["priority_score"],
            -item["gap"],
            item["competency_name"],
        )
    )

    # ---------------------------------------------------------
    # 5. Generate fresh recommendations
    # ---------------------------------------------------------
    recommendations = []

    for role_competency in role_competencies:

        current_level = current_levels.get(
            role_competency.competency_id,
            1,
        )

        required_level = role_competency.required_level

        gap = max(
            required_level - current_level,
            0,
        )

        # No gap -> no recommendation
        if gap == 0:
            continue

        criticality_weight = (
            2 if role_competency.is_critical else 0
        )

        priority_score = (
            (gap * 2)
            + criticality_weight
            + role_competency.organizational_priority
        )

        # -----------------------------------------------------
        # Find courses above current competency level
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
        # Prefer courses that reach the required level
        # -----------------------------------------------------
        reaching_required = [
            mapping
            for mapping in course_mappings
            if mapping.target_level >= required_level
        ]

        if reaching_required:
            eligible_courses = reaching_required
        else:
            # No course reaches required level.
            # Use the highest available stepping-stone.
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
        # Best course-level fit first
        # -----------------------------------------------------
        eligible_courses.sort(
            key=lambda mapping: (
                abs(
                    mapping.target_level
                    - required_level
                ),
                -mapping.target_level,
            )
        )

        competency = db.get(
            Competency,
            role_competency.competency_id,
        )

        if not competency:
            continue

        # -----------------------------------------------------
        # Add recommendations
        # -----------------------------------------------------
        for mapping in eligible_courses:

            course = db.get(
                Course,
                mapping.course_id,
            )

            if not course:
                continue

            reason = (
                f"Current level: {current_level}, "
                f"Required level: {required_level}, "
                f"Gap: {gap}, "
                f"Course target level: "
                f"{mapping.target_level}."
            )

            recommendations.append(
                {
                    "course_id": course.id,
                    "course_title": course.title,
                    "provider": course.provider,
                    "source": course.source,
                    "url": course.url,
                    "duration_minutes": course.duration_minutes,
                    "course_level": course.level,
                    "competency_id": competency.id,
                    "competency_name": competency.name,
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

    # ---------------------------------------------------------
    # Global recommendation ranking
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

    # ---------------------------------------------------------
    # 6. Dashboard summary
    # ---------------------------------------------------------
    total_competencies = len(competencies)

    competencies_with_gaps = sum(
        1
        for item in competencies
        if item["gap"] > 0
    )

    mastered_competencies = sum(
        1
        for item in competencies
        if item["gap"] == 0
    )

    # ---------------------------------------------------------
    # 7. Return dashboard
    # ---------------------------------------------------------
    return {
        "employee": {
            "user_id": current_user.id,
            "email": current_user.email,
            "role_id": role.id,
            "role_name": role.name,
        },
        "summary": {
            "total_competencies": total_competencies,
            "competencies_with_gaps": competencies_with_gaps,
            "mastered_competencies": mastered_competencies,
            "total_recommendations": len(recommendations),
        },
        "competencies": competencies,
        "priority_gaps": priority_gaps,
        "recommendations": recommendations,
    }