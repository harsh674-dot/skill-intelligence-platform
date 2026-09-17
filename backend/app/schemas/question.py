import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    competency_id: uuid.UUID
    question_text: str
    question_type: str
    difficulty: str
    options: dict
    explanation: str | None
    source_content_id: uuid.UUID | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class QuestionCreateRequest(BaseModel):
    competency_id: uuid.UUID
    question_text: str
    question_type: str = "mcq"
    difficulty: str = "beginner"
    options: dict
    correct_answer: str
    explanation: str | None = None
    bloom_tag: str | None = None


class QuestionUpdateRequest(BaseModel):
    question_text: str | None = None
    options: dict | None = None
    correct_answer: str | None = None
    explanation: str | None = None
    bloom_tag: str | None = None
    difficulty: str | None = None
