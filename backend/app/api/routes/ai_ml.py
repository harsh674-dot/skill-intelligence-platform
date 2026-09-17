import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models.ai_ml import ModelGovernance, CompetencyMapping
from app.schemas.ai_ml import ModelGovernanceResponse, CompetencyMappingResponse
from app.services.model_governance import ModelGovernanceService

router = APIRouter(
    prefix="/ai",
    tags=["AI/ML Governance"],
)


@router.get("/mappings")
def list_mappings(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """List all competency mappings."""
    mappings = db.query(CompetencyMapping).all()
    return [
        CompetencyMappingResponse(
            id=m.id,
            role_id=m.role_id,
            competency_id=m.competency_id,
            mapping_type=m.mapping_type,
            confidence=m.confidence,
            source=m.source,
            model_version=m.model_version,
            last_updated=m.last_updated,
        )
        for m in mappings
    ]


@router.post("/mappings")
def create_mapping(
    role_id: uuid.UUID,
    competency_id: uuid.UUID,
    required_level: int,
    mapping_type: str = "hybrid",
    is_critical: bool = False,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Create or update a competency mapping."""
    from app.services.competency_mapping import update_competency_mapping
    result = update_competency_mapping(
        db, str(role_id), str(competency_id), required_level, is_critical
    )
    return result


@router.get("/governance")
def list_governance_logs(
    model_name: str = None,
    model_type: str = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """List AI model governance logs."""
    service = ModelGovernanceService(db)
    logs = service.list_logs(model_name, model_type, limit)
    return [
        ModelGovernanceResponse(
            id=l.id,
            model_name=l.model_name,
            model_version=l.model_version,
            model_type=l.model_type,
            input_hash=l.input_hash,
            output_summary=l.output_summary,
            latency_ms=l.latency_ms,
            is_approved=l.is_approved,
            reviewed_by=l.reviewed_by,
            review_notes=l.review_notes,
            created_at=l.created_at,
        )
        for l in logs
    ]


@router.post("/governance/{governance_id}/approve")
def approve_governance(
    governance_id: str,
    reviewed_by: str,
    notes: str = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Approve an AI model inference."""
    service = ModelGovernanceService(db)
    return service.approve_inference(governance_id, reviewed_by, notes)


@router.post("/governance/{governance_id}/reject")
def reject_governance(
    governance_id: str,
    reviewed_by: str,
    notes: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Reject an AI model inference."""
    service = ModelGovernanceService(db)
    return service.reject_inference(governance_id, reviewed_by, notes)
