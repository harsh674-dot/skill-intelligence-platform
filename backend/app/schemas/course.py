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


class CourseCreateRequest(BaseModel):
    title: str
    description: str | None = None
    provider: str | None = None
    source: str = "admin_upload"
    external_id: str | None = None
    url: str | None = None
    duration_minutes: int | None = None
    level: str | None = None


class CourseUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    provider: str | None = None
    source: str | None = None
    external_id: str | None = None
    url: str | None = None
    duration_minutes: int | None = None
    level: str | None = None