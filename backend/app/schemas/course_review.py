import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CourseReviewCreate(BaseModel):
    helpfulness_rating: int = Field(ge=1, le=5)
    comments: str | None = Field(default=None, max_length=5000)


class CourseReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    user_name: str
    course_id: uuid.UUID
    helpfulness_rating: int
    comments: str | None = None
    created_at: datetime


class CourseReviewStats(BaseModel):
    course_id: uuid.UUID
    average_helpfulness: float
    total_reviews: int
    reviews: list[CourseReviewResponse] = []
