import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DPDPConsentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    purpose: str
    consent_given: bool
    consent_date: datetime | None
    withdrawn_date: datetime | None
    legal_basis: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class DPDPConsentUpdateRequest(BaseModel):
    consent_given: bool
    legal_basis: str | None = None
    notes: str | None = None
