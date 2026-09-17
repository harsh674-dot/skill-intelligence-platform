import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CompetencyMappingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role_id: uuid.UUID
    competency_id: uuid.UUID
    mapping_type: str
    confidence: float
    source: str
    model_version: str | None
    last_updated: datetime


class ModelGovernanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    model_name: str
    model_version: str
    model_type: str
    input_hash: str | None
    output_summary: dict | None
    latency_ms: float | None
    is_approved: bool
    reviewed_by: str | None
    review_notes: str | None
    created_at: datetime
