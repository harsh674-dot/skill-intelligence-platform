import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CompetencyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    domain: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime