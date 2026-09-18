import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class ExperienceReviewCreate(BaseModel):
    category: Literal["platform", "training_program", "onboarding"]
    rating: int = Field(ge=1, le=5)
    comments: str | None = Field(default=None, max_length=5000)


class ExperienceReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    user_name: str
    user_role: str
    category: str
    rating: int
    comments: str | None = None
    created_at: datetime


class CategoryAggregation(BaseModel):
    category: str
    average_rating: float
    total_reviews: int
    distribution: dict[str, int]


class ExperienceReviewAggregatedResponse(BaseModel):
    overall_average: float
    total_reviews: int
    categories: list[CategoryAggregation]
    recent_reviews: list[ExperienceReviewResponse] = []
