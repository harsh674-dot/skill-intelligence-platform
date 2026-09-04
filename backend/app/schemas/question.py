import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    competency_id: uuid.UUID
    question_text: str
    question_type: str
    difficulty: str
    options: Any
    explanation: str | None
    source_content_id: uuid.UUID | None
    is_active: bool
    created_at: datetime
    updated_at: datetime