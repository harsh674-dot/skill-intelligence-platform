import os
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models.user import User
from app.models.profile import OfficialProfile
from app.schemas.profile import OfficialProfileResponse
from app.schemas.profile import (
    OfficialProfileResponse as ProfileResponse,
)
from app.services.predictive_analytics import PredictiveAnalyticsService
from app.services.sso_auth import SSOAdapter

router = APIRouter(
    prefix="/admin",
    tags=["Admin & Analytics"],
)

sso_adapter = SSOAdapter()


@router.get("/profiles")
def admin_list_profiles(
    department: str = None,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Admin-only: List all official profiles."""
    stmt = select(OfficialProfile).order_by(OfficialProfile.created_at.desc()).limit(limit)
    if department:
        stmt = stmt.where(OfficialProfile.department == department)
    profiles = db.scalars(stmt).all()
    return [ProfileResponse.from_orm(p) for p in profiles]


@router.get("/predict/skill-gaps")
def admin_predict_skill_gaps(
    department: str = Query(None),
    timeframe_months: int = Query(6, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Admin-only: Predict skill gaps organization-wide."""
    service = PredictiveAnalyticsService(db)
    return service.predict_skill_gaps(department, timeframe_months)


@router.get("/predict/course-success")
def admin_predict_course_success(
    course_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Admin-only: Predict course success probability."""
    service = PredictiveAnalyticsService(db)
    return service.predict_course_success(course_id, user_id)


@router.get("/predict/heatmap")
def admin_skill_heatmap(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Admin-only: Organization-wide skill heatmap."""
    service = PredictiveAnalyticsService(db)
    return service.organization_skill_heatmap()


@router.get("/sso/status")
def sso_status(db: Session = Depends(get_db), current_user=Depends(require_admin)):
    """Check SSO configuration and authentication status."""
    adapter = SSOAdapter()
    demo_token = adapter.generate_demo_token(
        email="admin@mospi.gov.in",
        name="Admin Official",
        department="Statistics",
        role="admin",
    )
    test_identity = adapter.authorize(demo_token)
    return {
        "enabled": adapter.enabled,
        "configured": adapter.is_configured(),
        "demo_mode": adapter.demo_mode,
        "jwt_available": True,
        "test_authorization": "success" if test_identity else "failed",
        "test_identity": test_identity if test_identity else None,
        "idp_url": adapter.idp_url if adapter.is_configured() else None,
        "token_endpoint": f"{adapter.idp_url}/oauth2/introspect" if adapter.is_configured() else None,
        "authorization_endpoint": adapter.get_authorization_url("https://localhost:8000/callback", "state") if adapter.is_configured() else None,
        "demo_token_sample": demo_token[:80] + "..." if demo_token else None,
    }


@router.get("/audit/{entity_type}/{entity_id}")
def get_entity_audit(
    entity_type: str,
    entity_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Get audit trail for a specific entity."""
    from app.services.model_governance import ModelGovernanceService
    service = ModelGovernanceService(db)
    return service.get_audit_trail(entity_type, entity_id)


@router.get("/predict/training-risk")
def admin_predict_training_risk(
    department: str = Query(None),
    threshold: float = Query(0.3, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Admin-only: Predict training failure risk."""
    service = PredictiveAnalyticsService(db)
    return service.predict_training_risk(department, threshold)


@router.get("/predict/retention")
def admin_predict_retention(
    department: str = Query(None),
    timeframe_days: int = Query(90, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Admin-only: Predict employee retention rate."""
    service = PredictiveAnalyticsService(db)
    return service.predict_retention(department, timeframe_days)


@router.get("/predict/role-fit/{user_id}")
def admin_predict_role_fit(
    user_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Admin-only: Predict user role fit score."""
    service = PredictiveAnalyticsService(db)
    return service.predict_role_fit(user_id)
