import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    course_id: uuid.UUID
    competency_id: uuid.UUID
    gap_score: float
    priority_score: float
    reason: str | None
    status: str
    created_at: datetime
    updated_at: datetime
