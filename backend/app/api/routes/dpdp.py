import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models.dpdp_consent import DPDPConsent
from app.models.user import User
from app.schemas.dpdp_consent import (
    DPDPConsentResponse,
    DPDPConsentUpdateRequest,
)

router = APIRouter(
    prefix="/dpdp",
    tags=["DPDP Compliance"],
)


@router.get(
    "/consent/{user_id}",
    response_model=DPDPConsentResponse,
)
def get_consent(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """
    Admin-only: Get DPDP consent record for a user.
    """
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    consent = db.scalar(
        select(DPDPConsent).where(DPDPConsent.user_id == user_id)
    )

    if not consent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No consent record found for this user",
        )

    return DPDPConsentResponse(
        id=consent.id,
        user_id=consent.user_id,
        purpose=consent.purpose,
        consent_given=consent.consent_given,
        consent_date=consent.consent_date,
        withdrawn_date=consent.withdrawn_date,
        legal_basis=consent.legal_basis,
        notes=consent.notes,
        created_at=consent.created_at,
        updated_at=consent.updated_at,
    )


@router.post(
    "/consent/{user_id}",
    response_model=DPDPConsentResponse,
)
def update_consent(
    user_id: uuid.UUID,
    update: DPDPConsentUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """
    Admin-only: Create or update DPDP consent for a user.
    """
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    consent = db.scalar(
        select(DPDPConsent).where(DPDPConsent.user_id == user_id)
    )

    now = datetime.now(timezone.utc)

    if consent:
        if not consent.consent_given and update.consent_given:
            consent.consent_date = now
        if consent.consent_given and not update.consent_given:
            consent.withdrawn_date = now
        consent.consent_given = update.consent_given
        consent.legal_basis = update.legal_basis
        consent.notes = update.notes
    else:
        consent = DPDPConsent(
            user_id=user_id,
            purpose="skill_intelligence_platform",
            consent_given=update.consent_given,
            consent_date=now if update.consent_given else None,
            withdrawn_date=now if not update.consent_given else None,
            legal_basis=update.legal_basis,
            notes=update.notes,
        )
        db.add(consent)

    db.commit()
    db.refresh(consent)

    return DPDPConsentResponse(
        id=consent.id,
        user_id=consent.user_id,
        purpose=consent.purpose,
        consent_given=consent.consent_given,
        consent_date=consent.consent_date,
        withdrawn_date=consent.withdrawn_date,
        legal_basis=consent.legal_basis,
        notes=consent.notes,
        created_at=consent.created_at,
        updated_at=consent.updated_at,
    )
