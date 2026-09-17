import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class AuthorSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    email: str
    designation: str | None = None
    department: str | None = None
    access_role: str


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=5000)


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    post_id: uuid.UUID
    author_id: uuid.UUID
    author: AuthorSummary
    body: str
    created_at: datetime
    updated_at: datetime


class PostCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    body: str = Field(min_length=5, max_length=20000)
    tags: list[str] = []


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    author_id: uuid.UUID
    author: AuthorSummary
    title: str
    body: str
    tags: list[str] = []
    created_at: datetime
    updated_at: datetime
    likes_count: int = 0
    comments_count: int = 0
    has_liked: bool = False


class PostDetailResponse(PostResponse):
    comments: list[CommentResponse] = []


class LikeToggleResponse(BaseModel):
    post_id: uuid.UUID
    liked: bool
    likes_count: int
