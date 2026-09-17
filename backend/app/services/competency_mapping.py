import json
import time
import logging
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.competency import Competency, RoleCompetency, UserCompetency
from app.models.course import Course, CourseCompetency
from app.models.learning import Recommendation

logger = logging.getLogger(__name__)


def competency_map_role(
    db: Session,
    role_id: str,
    mapping_type: str = "hybrid",
) -> dict:
    """
    Competency Mapping Model (Section 4.1):
    Hybrid rule-based + ML classifier mapping role -> competency matrix.
    
    In production this would train a classifier on historical data.
    In this implementation it combines rule-based benchmark data with
    confidence scoring.
    """
    role = db.get(CompetencyMapping, role_id)
    if not role:
        return {"error": "Role not found", "role_id": role_id}

    role_competencies = (
        db.query(RoleCompetency)
        .filter(RoleCompetency.role_id == role_id)
        .all()
    )

    mappings = []
    for rc in role_competencies:
        comp = db.get(Competency, rc.competency_id)
        if comp:
            mappings.append({
                "competency_id": str(comp.id),
                "competency_name": comp.name,
                "domain": comp.domain,
                "required_level": rc.required_level,
                "is_critical": rc.is_critical,
                "mapping_type": mapping_type,
                "confidence": rc.required_level / 5.0,
                "source": "rule_based + role_definition",
            })

    return {
        "role_id": role_id,
        "mapping_type": mapping_type,
        "total_competencies": len(mappings),
        "mappings": mappings,
    }


def update_competency_mapping(
    db: Session,
    role_id: str,
    competency_id: str,
    required_level: int,
    is_critical: bool = False,
    priority: int = 1,
) -> dict:
    """Update or create a competency mapping for a role."""
    existing = db.execute(
        select(RoleCompetency).where(
            RoleCompetency.role_id == role_id,
            RoleCompetency.competency_id == competency_id,
        )
    ).scalar_one_or_none()

    if existing:
        existing.required_level = required_level
        existing.is_critical = is_critical
        existing.organizational_priority = priority
    else:
        from app.models.competency import RoleCompetency as RC
        rc = RC(
            role_id=role_id,
            competency_id=competency_id,
            required_level=required_level,
            is_critical=is_critical,
            organizational_priority=priority,
        )
        db.add(rc)

    db.commit()
    return {"status": "updated", "role_id": role_id, "competency_id": competency_id}
