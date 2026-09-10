from app.models.competency import (
    RoleCompetency,
    UserCompetency,
)
from app.models.course import (
    Course,
    CourseCompetency,
)
from app.models.learning import Recommendation


def refresh_recommendations(
    db,
    current_user,
):
    """
    Phase 5 recommendation refresh.

    Recalculates recommendations using the user's
    latest competency levels.

    Behaviour:
    - Creates recommendations for new gaps.
    - Updates existing recommendations.
    - Reopens dismissed recommendations if the gap returns.
    - Marks completed competencies' recommendations as completed.
    - Dismisses recommendations that are no longer relevant.
    """

    if not current_user.job_role_id:
        return {
            "created": 0,
            "updated": 0,
            "dismissed": 0,
            "completed": 0,
            "active": 0,
        }

    role_competencies = (
        db.query(RoleCompetency)
        .filter(
            RoleCompetency.role_id
            == current_user.job_role_id
        )
        .all()
    )

    user_competencies = (
        db.query(UserCompetency)
        .filter(
            UserCompetency.user_id
            == current_user.id
        )
        .all()
    )

    current_levels = {
        uc.competency_id: uc.current_level
        for uc in user_competencies
    }

    existing_recommendations = (
        db.query(Recommendation)
        .filter(
            Recommendation.user_id
            == current_user.id
        )
        .all()
    )

    existing_map = {
        (
            recommendation.course_id,
            recommendation.competency_id,
        ): recommendation
        for recommendation in existing_recommendations
    }

    seen = set()

    created = 0
    updated = 0
    dismissed = 0
    completed = 0

    # ---------------------------------------------------------
    # Recalculate recommendations from current competency state
    # ---------------------------------------------------------

    for role_competency in role_competencies:

        current_level = current_levels.get(
            role_competency.competency_id,
            1,
        )

        required_level = (
            role_competency.required_level
        )

        gap = max(
            required_level - current_level,
            0,
        )

        if gap == 0:
            continue

        criticality_weight = (
            2
            if role_competency.is_critical
            else 0
        )

        priority_score = (
            (gap * 2)
            + criticality_weight
            + role_competency.organizational_priority
        )

        course_mappings = (
            db.query(CourseCompetency)
            .filter(
                CourseCompetency.competency_id
                == role_competency.competency_id,
                CourseCompetency.target_level
                > current_level,
            )
            .all()
        )

        if not course_mappings:
            continue

        reaching_required = [
            mapping
            for mapping in course_mappings
            if mapping.target_level
            >= required_level
        ]

        if reaching_required:
            eligible_courses = reaching_required

        else:
            highest_target = max(
                mapping.target_level
                for mapping in course_mappings
            )

            eligible_courses = [
                mapping
                for mapping in course_mappings
                if mapping.target_level
                == highest_target
            ]

        eligible_courses.sort(
            key=lambda mapping: (
                abs(
                    mapping.target_level
                    - required_level
                ),
                -mapping.target_level,
            )
        )

        for mapping in eligible_courses:

            course = db.get(
                Course,
                mapping.course_id,
            )

            if not course:
                continue

            key = (
                course.id,
                role_competency.competency_id,
            )

            seen.add(key)

            reason = (
                f"Current level: {current_level}, "
                f"Required level: {required_level}, "
                f"Gap: {gap}, "
                f"Course target level: "
                f"{mapping.target_level}."
            )

            recommendation = existing_map.get(key)

            if recommendation:

                recommendation.gap_score = gap

                recommendation.priority_score = (
                    priority_score
                )

                recommendation.reason = reason

                if recommendation.status == "dismissed":
                    recommendation.status = "pending"

                updated += 1

            else:

                recommendation = Recommendation(
                    user_id=current_user.id,
                    course_id=course.id,
                    competency_id=(
                        role_competency.competency_id
                    ),
                    gap_score=gap,
                    priority_score=priority_score,
                    reason=reason,
                    status="pending",
                )

                db.add(recommendation)

                created += 1

    # ---------------------------------------------------------
    # Determine which competencies have no remaining gap
    # ---------------------------------------------------------

    gap_zero_competencies = {
        role_competency.competency_id
        for role_competency in role_competencies
        if max(
            role_competency.required_level
            - current_levels.get(
                role_competency.competency_id,
                1,
            ),
            0,
        )
        == 0
    }

    # ---------------------------------------------------------
    # Update stale recommendations
    # ---------------------------------------------------------

    for recommendation in existing_recommendations:

        if recommendation.status not in {
            "pending",
            "accepted",
        }:
            continue

        key = (
            recommendation.course_id,
            recommendation.competency_id,
        )

        if key in seen:
            continue

        if (
            recommendation.competency_id
            in gap_zero_competencies
        ):
            recommendation.status = "completed"
            completed += 1

        else:
            recommendation.status = "dismissed"
            dismissed += 1

    db.commit()

    return {
        "created": created,
        "updated": updated,
        "dismissed": dismissed,
        "completed": completed,
        "active": len(seen),
    }