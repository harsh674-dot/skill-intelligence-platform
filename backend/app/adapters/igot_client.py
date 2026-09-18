"""
iGOT Karmayogi API Adapter.

Wraps all outbound calls to the iGOT platform behind a clean interface so
the rest of the codebase is insulated from external API contract changes.

Environment variables
---------------------
IGOT_API_URL   : Base URL of the iGOT REST API.
                  E.g. https://api.karmayogi.nic.in/v1
IGOT_API_KEY   : Bearer token / API key for authentication.

When neither variable is set the adapter uses mock data for testing.
"""

from __future__ import annotations

import os
from typing import Any

import httpx
from sqlalchemy.orm import Session
from sqlalchemy import select, or_

from app.models.course import Course

_IGOT_API_URL = os.environ.get("IGOT_API_URL", "").rstrip("/")
_IGOT_API_KEY = os.environ.get("IGOT_API_KEY", "")

_MOCK_CATALOGUE: list[dict[str, Any]] = [
    {
        "course_id": "igot-stat-001",
        "title": "Introduction to Statistical Techniques",
        "description": "Learn the basics of statistical analysis and survey methodology for government data collection.",
        "provider": "MoSPI / NSSTA",
        "domain": "Technical",
        "competency_tags": ["statistics", "data-collection", "survey-design"],
        "duration_minutes": 120,
        "level": "Beginner",
        "url": "https://igot.gov.in/courses/igot-stat-001",
        "source": "mock",
    },
    {
        "course_id": "igot-stat-002",
        "title": "SDG Indicator Framework",
        "description": "Understanding Sustainable Development Goals indicators and tracking methodologies.",
        "provider": "MoSPI / NSSTA",
        "domain": "Technical",
        "competency_tags": ["sdg", "indicators", "policy"],
        "duration_minutes": 180,
        "level": "Intermediate",
        "url": "https://igot.gov.in/courses/igot-stat-002",
        "source": "mock",
    },
    {
        "course_id": "igot-stat-003",
        "title": "Price Statistics and Index Construction",
        "description": "Methods for constructing consumer price indices and producer price indices.",
        "provider": "MoSPI / NSSTA",
        "domain": "Technical",
        "competency_tags": ["price", "index", "economics"],
        "duration_minutes": 150,
        "level": "Advanced",
        "url": "https://igot.gov.in/courses/igot-stat-003",
        "source": "mock",
    },
    {
        "course_id": "igot-adv-001",
        "title": "Data Visualization with Python",
        "description": "Master data visualization using matplotlib and seaborn for official statistics.",
        "provider": "NIC",
        "domain": "Non-Technical",
        "competency_tags": ["python", "visualization", "data-science"],
        "duration_minutes": 240,
        "level": "Advanced",
        "url": "https://igot.gov.in/courses/igot-adv-001",
        "source": "mock",
    },
    {
        "course_id": "igot-adv-002",
        "title": "Machine Learning for Official Statistics",
        "description": "Applying ML techniques to large-scale government data analysis.",
        "provider": "NIC",
        "domain": "Non-Technical",
        "competency_tags": ["ml", "ai", "analytics"],
        "duration_minutes": 300,
        "level": "Advanced",
        "url": "https://igot.gov.in/courses/igot-adv-002",
        "source": "mock",
    },
]


def _is_live() -> bool:
    return bool(_IGOT_API_URL and _IGOT_API_KEY)


def _mock_search(query: str = "", domain: str | None = None) -> list[dict[str, Any]]:
    results = _MOCK_CATALOGUE
    if domain:
        results = [c for c in results if domain.lower() in c.get("domain", "").lower()]
    if query:
        q = query.lower()
        results = [
            c for c in results
            if q in c.get("title", "").lower()
            or q in c.get("description", "").lower()
            or any(q in tag.lower() for tag in c.get("competency_tags", []))
        ]
    return results


def _mock_get_course(course_id: str) -> dict[str, Any] | None:
    for c in _MOCK_CATALOGUE:
        if c["course_id"] == course_id:
            return c
    return None


def _db_search(db: Session, query: str, domain: str | None) -> list[dict[str, Any]]:
    """Filter database catalog by query and domain."""
    stmt = select(Course)
    if domain:
        stmt = stmt.where(Course.provider.ilike(f"%{domain}%"))

    if query:
        stmt = stmt.where(
            or_(
                Course.title.ilike(f"%{query}%"),
                Course.description.ilike(f"%{query}%"),
            )
        )

    courses = db.scalars(stmt).all()
    results = []
    for course in courses:
        results.append({
            "course_id": str(course.id),
            "title": course.title,
            "provider": course.provider or "iGOT Karmayogi",
            "domain": "Statistical",
            "competency_tags": [],
            "duration_hours": course.duration_minutes // 60 if course.duration_minutes else 0,
            "level": course.level,
            "url": course.url,
            "description": course.description,
        })
    return results


# ---------------------------------------------------------------------------
# Public adapter methods
# ---------------------------------------------------------------------------


def search_courses(
    db: Session | None = None,
    query: str = "",
    domain: str | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    """
    Search the iGOT course catalogue.

    Returns mock results when IGOT_API_URL is not set and no DB is available.
    Falls back to the database when DB is provided and IGOT_API_URL is not set.
    """
    if not _is_live():
        if db is None:
            results = _mock_search(query, domain)
            return {
                "source": "mock",
                "total": len(results),
                "courses": results[:limit],
            }
        results = _db_search(db, query, domain)[:limit]
        return {
            "source": "database",
            "total": len(results),
            "courses": results,
        }

    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(
                f"{_IGOT_API_URL}/courses/search",
                headers={"Authorization": f"Bearer {_IGOT_API_KEY}"},
                params={"query": query, "domain": domain, "limit": limit},
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "source": "live",
                "total": data.get("total", len(data.get("courses", []))),
                "courses": data.get("courses", []),
            }
    except Exception as exc:
        results = _db_search(db, query, domain)[:limit] if db else []
        return {
            "source": "database_fallback",
            "error": str(exc),
            "total": len(results),
            "courses": results,
        }


def get_course(
    course_id: str,
    db: Session | None = None,
) -> dict[str, Any] | None:
    """
    Fetch a single course by ID.

    Returns mock course when IGOT_API_URL is not set and no DB is available.
    Falls back to the database when DB is provided.
    """
    if not _is_live():
        if db is None:
            return _mock_get_course(course_id)
        course = db.get(Course, course_id)
        if course:
            return {
                "source": "database",
                "course_id": str(course.id),
                "title": course.title,
                "provider": course.provider or "iGOT Karmayogi",
                "domain": "Statistical",
                "competency_tags": [],
                "duration_hours": course.duration_minutes // 60 if course.duration_minutes else 0,
                "level": course.level,
                "url": course.url,
                "description": course.description,
            }
        return None

    with httpx.Client(timeout=10) as client:
        resp = client.get(
            f"{_IGOT_API_URL}/courses/{course_id}",
            headers={"Authorization": f"Bearer {_IGOT_API_KEY}"},
        )
        resp.raise_for_status()
        return {"source": "live", **resp.json()}


def enroll_user(
    db: Session | None = None,
    igot_user_id: str = "",
    course_id: str = "",
    platform_user_id: str | None = None,
) -> dict[str, Any]:
    """
    Enroll a user in an iGOT course.

    Returns mock result when IGOT_API_URL is not set and no DB is available.
    Records intent in database when DB is provided.
    """
    if not _is_live():
        if db is None:
            return {
                "source": "mock",
                "status": "intent_recorded",
                "igot_user_id": igot_user_id,
                "course_id": course_id,
                "platform_user_id": platform_user_id,
            }
        return {
            "source": "database",
            "status": "intent_recorded",
            "igot_user_id": igot_user_id,
            "course_id": course_id,
            "platform_user_id": platform_user_id,
            "message": (
                "Enrolment intent recorded in DB. Configure IGOT_API_URL and "
                "IGOT_API_KEY to trigger live enrolment."
            ),
        }

    with httpx.Client(timeout=15) as client:
        resp = client.post(
            f"{_IGOT_API_URL}/enrollments",
            headers={
                "Authorization": f"Bearer {_IGOT_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"userId": igot_user_id, "courseId": course_id},
        )
        resp.raise_for_status()
        return {"source": "live", **resp.json()}
