import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None
    provider: str | None
    source: str
    external_id: str | None
    url: str | None
    duration_minutes: int | None
    level: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime