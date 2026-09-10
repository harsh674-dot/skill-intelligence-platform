import uuid

from pydantic import BaseModel, Field, model_validator


class AnswerSubmitRequest(BaseModel):
    question_id: uuid.UUID
    selected_answer: str | None = None
    selected_option: str | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_selection(cls, values):
        if isinstance(values, dict):
            answer = values.get("selected_answer") or values.get("selected_option")
            if not answer:
                raise ValueError("selected_answer or selected_option is required")
            values["selected_answer"] = answer
        return values


class AnswerSubmitResponse(BaseModel):
    answer_id: uuid.UUID
    assessment_id: uuid.UUID
    question_id: uuid.UUID
    selected_answer: str
    saved: bool
    is_correct: bool | None = None
    explanation: str | None = None