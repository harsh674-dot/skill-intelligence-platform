import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class OfficialProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    designation: str | None
    department: str | None
    cadre: str | None
    job_role_id: uuid.UUID | None
    education: str | None
    experience_years: int | None
    prior_trainings: list | None
    self_declared_competencies: list | None
    profile_confidence: float
    data_source: str
    is_complete: bool
    created_at: datetime
    updated_at: datetime


class CompetencyAssessmentRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    profile_id: uuid.UUID
    competency_id: uuid.UUID
    proficiency_score: float
    proficiency_level: int
    source: str
    confidence: float
    assessed_at: datetime


class LearningEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    profile_id: uuid.UUID
    course_id: uuid.UUID | None
    event_type: str
    status: str
    score: float | None
    external_id: str | None
    created_at: datetime
