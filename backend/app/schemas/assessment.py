import uuid

from pydantic import BaseModel, Field


class AnswerSubmitRequest(BaseModel):
    question_id: uuid.UUID
    selected_answer: str = Field(min_length=1, max_length=255)


class AnswerSubmitResponse(BaseModel):
    answer_id: uuid.UUID
    assessment_id: uuid.UUID
    question_id: uuid.UUID
    selected_answer: str
    saved: bool