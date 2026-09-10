import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models.competency import (
    Competency,
    RoleCompetency,
    UserCompetency,
)
from app.models.course import Course, CourseCompetency
from app.models.role import Role
from app.models.user import User
from app.models.assessment import Assessment


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


PROFICIENCY_LABELS = {
    1: "Beginner",
    2: "Basic",
    3: "Intermediate",
    4: "Advanced",
    5: "Expert",
}

# High performance in-memory cache: key -> (timestamp, data)
_EMPLOYEE_DASHBOARD_CACHE: dict[str, tuple[float, dict]] = {}
_ADMIN_DASHBOARD_CACHE: dict[str, tuple[float, dict]] = {}
CACHE_TTL_SECONDS = 30.0


def invalidate_dashboard_cache(user_id: str | None = None):
    """Invalidate dashboard caches when assessments or competencies change."""
    if user_id:
        keys_to_remove = [k for k in _EMPLOYEE_DASHBOARD_CACHE if k.startswith(str(user_id))]
        for k in keys_to_remove:
            _EMPLOYEE_DASHBOARD_CACHE.pop(k, None)
    else:
        _EMPLOYEE_DASHBOARD_CACHE.clear()
    _ADMIN_DASHBOARD_CACHE.clear()


@router.get("")
def get_employee_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    cache_key = f"{current_user.id}_{current_user.job_role_id}"
    now = time.time()
    if cache_key in _EMPLOYEE_DASHBOARD_CACHE:
        cached_time, cached_data = _EMPLOYEE_DASHBOARD_CACHE[cache_key]
        if now - cached_time < CACHE_TTL_SECONDS:
            return cached_data

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
    # 2. Batch fetch role competencies and user levels
    # ---------------------------------------------------------
    role_competencies = (
        db.query(RoleCompetency)
        .filter(RoleCompetency.role_id == current_user.job_role_id)
        .all()
    )

    user_competencies = (
        db.query(UserCompetency)
        .filter(UserCompetency.user_id == current_user.id)
        .all()
    )

    current_levels = {
        uc.competency_id: uc.current_level
        for uc in user_competencies
    }

    # ---------------------------------------------------------
    # 3. High-Speed Batch Fetching (Eliminates 50+ N+1 queries)
    # ---------------------------------------------------------
    comp_ids = [rc.competency_id for rc in role_competencies]

    competencies_list = (
        db.query(Competency)
        .filter(Competency.id.in_(comp_ids))
        .all()
    ) if comp_ids else []
    comp_map = {c.id: c for c in competencies_list}

    all_course_mappings = (
        db.query(CourseCompetency)
        .filter(CourseCompetency.competency_id.in_(comp_ids))
        .all()
    ) if comp_ids else []

    course_mappings_by_comp: dict[str, list[CourseCompetency]] = {}
    for cm in all_course_mappings:
        course_mappings_by_comp.setdefault(cm.competency_id, []).append(cm)

    needed_course_ids = {cm.course_id for cm in all_course_mappings}
    courses_list = (
        db.query(Course)
        .filter(Course.id.in_(needed_course_ids))
        .all()
    ) if needed_course_ids else []
    course_map = {c.id: c for c in courses_list}

    # ---------------------------------------------------------
    # 4. Build competency dashboard (In Memory - Instant)
    # ---------------------------------------------------------
    competencies = []
    priority_gaps = []

    for role_competency in role_competencies:
        competency = comp_map.get(role_competency.competency_id)
        if not competency:
            continue

        current_level = current_levels.get(
            role_competency.competency_id,
            1,
        )
        required_level = role_competency.required_level
        gap = max(required_level - current_level, 0)
        criticality_weight = 2 if role_competency.is_critical else 0
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
            "organizational_priority": role_competency.organizational_priority,
            "priority_score": priority_score,
        }

        competencies.append(competency_data)
        if gap > 0:
            priority_gaps.append(competency_data)

    priority_gaps.sort(
        key=lambda item: (
            -item["priority_score"],
            -item["gap"],
            item["competency_name"],
        )
    )

    # ---------------------------------------------------------
    # 5. Generate fresh recommendations (In Memory - Instant)
    # ---------------------------------------------------------
    recommendations = []

    for role_competency in role_competencies:
        current_level = current_levels.get(role_competency.competency_id, 1)
        required_level = role_competency.required_level
        gap = max(required_level - current_level, 0)
        if gap == 0:
            continue

        criticality_weight = 2 if role_competency.is_critical else 0
        priority_score = (
            (gap * 2)
            + criticality_weight
            + role_competency.organizational_priority
        )

        comp_cms = course_mappings_by_comp.get(role_competency.competency_id, [])
        course_mappings = [
            mapping for mapping in comp_cms
            if mapping.target_level > current_level
        ]

        if not course_mappings:
            continue

        reaching_required = [
            mapping for mapping in course_mappings
            if mapping.target_level >= required_level
        ]

        if reaching_required:
            eligible_courses = reaching_required
        else:
            highest_target = max(mapping.target_level for mapping in course_mappings)
            eligible_courses = [
                mapping for mapping in course_mappings
                if mapping.target_level == highest_target
            ]

        eligible_courses.sort(
            key=lambda mapping: (
                abs(mapping.target_level - required_level),
                -mapping.target_level,
            )
        )

        competency = comp_map.get(role_competency.competency_id)
        if not competency:
            continue

        for mapping in eligible_courses:
            course = course_map.get(mapping.course_id)
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
    # 7. Return dashboard & populate cache
    # ---------------------------------------------------------
    dashboard_result = {
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

    _EMPLOYEE_DASHBOARD_CACHE[cache_key] = (now, dashboard_result)
    return dashboard_result


@router.get("/admin")
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Phase 6 Admin & Workforce Analytics.
    Aggregates skill gaps, proficiency distribution, learning progress,
    and training effectiveness across the organization.
    """
    now = time.time()
    if "admin" in _ADMIN_DASHBOARD_CACHE:
        cached_time, cached_data = _ADMIN_DASHBOARD_CACHE["admin"]
        if now - cached_time < CACHE_TTL_SECONDS:
            return cached_data

    users = db.query(User).filter(User.is_active == True).all()
    total_employees = sum(1 for u in users if u.access_role == "employee")
    roles = db.query(Role).filter(Role.is_active == True).all()
    roles_map = {r.id: r.name for r in roles}

    # Department breakdown
    dept_counts: dict[str, int] = {}
    for u in users:
        dept = u.department or "Unassigned"
        dept_counts[dept] = dept_counts.get(dept, 0) + 1

    # Role breakdown
    role_counts: dict[str, int] = {}
    for u in users:
        r_name = roles_map.get(u.job_role_id, "Unassigned")
        role_counts[r_name] = role_counts.get(r_name, 0) + 1

    # Competency aggregation
    all_competencies = db.query(Competency).filter(Competency.is_active == True).all()
    comp_map = {c.id: c for c in all_competencies}

    role_comps = db.query(RoleCompetency).all()

    user_comps = db.query(UserCompetency).all()
    user_comp_map = {}
    for uc in user_comps:
        user_comp_map[(uc.user_id, uc.competency_id)] = uc.current_level

    # Compute gaps across all employees with roles
    gap_stats_by_competency: dict = {}
    level_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    domain_scores: dict[str, int] = {}
    domain_counts: dict[str, int] = {}

    total_gaps_count = 0
    total_gap_magnitude = 0
    critical_gaps_count = 0

    for u in users:
        if u.access_role != "employee" or not u.job_role_id:
            continue

        for rc in role_comps:
            if rc.role_id != u.job_role_id:
                continue

            c = comp_map.get(rc.competency_id)
            if not c:
                continue

            curr_lvl = user_comp_map.get((u.id, rc.competency_id), 1)
            level_distribution[curr_lvl] = level_distribution.get(curr_lvl, 0) + 1

            dom = c.domain or "General"
            domain_scores[dom] = domain_scores.get(dom, 0) + curr_lvl
            domain_counts[dom] = domain_counts.get(dom, 0) + 1

            gap = max(rc.required_level - curr_lvl, 0)
            if gap > 0:
                total_gaps_count += 1
                total_gap_magnitude += gap
                if rc.is_critical:
                    critical_gaps_count += 1

                crit_weight = 2 if rc.is_critical else 0
                pri = (gap * 2) + crit_weight + rc.organizational_priority

                if c.id not in gap_stats_by_competency:
                    gap_stats_by_competency[c.id] = {
                        "competency_id": str(c.id),
                        "competency_name": c.name,
                        "domain": c.domain,
                        "affected_employees": 0,
                        "total_gap": 0,
                        "total_priority": 0,
                        "is_critical": rc.is_critical,
                    }
                gap_stats_by_competency[c.id]["affected_employees"] += 1
                gap_stats_by_competency[c.id]["total_gap"] += gap
                gap_stats_by_competency[c.id]["total_priority"] += pri

    # Top organizational deficits
    top_deficits = sorted(
        gap_stats_by_competency.values(),
        key=lambda x: (-x["total_priority"], -x["total_gap"], -x["affected_employees"]),
    )[:8]

    # Domain average proficiency
    domain_health = []
    for dom, total_pts in domain_scores.items():
        cnt = domain_counts.get(dom, 1)
        avg_lvl = round(total_pts / cnt, 2)
        domain_health.append({
            "domain": dom,
            "average_level": avg_lvl,
            "label": PROFICIENCY_LABELS.get(round(avg_lvl), "Intermediate"),
            "evaluated_count": cnt,
        })

    # Assessments and Training Effectiveness
    assessments = db.query(Assessment).all()
    completed_assessments = [a for a in assessments if a.status == "completed"]
    reassessments = [a for a in completed_assessments if a.assessment_type == "reassessment"]
    avg_score = (
        round(sum(a.score or 0 for a in completed_assessments) / len(completed_assessments), 1)
        if completed_assessments
        else 0.0
    )

    # Content & AI questions
    from app.models.learning import LearningContent
    from app.models.ai_question import AIGeneratedQuestion

    total_content = db.query(LearningContent).count()
    ai_questions = db.query(AIGeneratedQuestion).all()
    ai_stats = {
        "total": len(ai_questions),
        "pending": sum(1 for q in ai_questions if q.status == "pending"),
        "approved": sum(1 for q in ai_questions if q.status == "approved"),
        "rejected": sum(1 for q in ai_questions if q.status == "rejected"),
    }

    admin_result = {
        "workforce_summary": {
            "total_employees": total_employees,
            "total_departments": len(dept_counts),
            "total_roles": len(roles),
            "departments": dept_counts,
            "roles": role_counts,
        },
        "gap_analytics": {
            "total_gaps_count": total_gaps_count,
            "critical_gaps_count": critical_gaps_count,
            "average_gap": (
                round(total_gap_magnitude / total_gaps_count, 2)
                if total_gaps_count
                else 0.0
            ),
            "top_deficits": top_deficits,
        },
        "proficiency_distribution": {
            label: level_distribution.get(lvl, 0)
            for lvl, label in PROFICIENCY_LABELS.items()
        },
        "domain_health": domain_health,
        "training_effectiveness": {
            "total_assessments": len(assessments),
            "completed_assessments": len(completed_assessments),
            "reassessments_taken": len(reassessments),
            "average_score": avg_score,
            "competency_upgrades": len(reassessments),
        },
        "content_and_ai": {
            "learning_materials": total_content,
            "ai_questions": ai_stats,
        },
    }

    _ADMIN_DASHBOARD_CACHE["admin"] = (now, admin_result)
    return admin_result