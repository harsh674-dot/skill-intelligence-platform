import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ChatSourceItem(BaseModel):
    chunk_id: str
    text: str
    similarity: float


class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    session_id: uuid.UUID
    user_id: uuid.UUID
    role: str
    content: str
    created_at: datetime


class ChatSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[ChatMessageResponse] = []


class ChatSessionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class ChatMessageRequest(BaseModel):
    session_id: uuid.UUID | None = None
    message: str = Field(min_length=1, max_length=2000)


class ChatMessageAnswer(BaseModel):
    session_id: uuid.UUID
    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse
    sources: list[ChatSourceItem] = []
    grounded_gaps: list[str] = []
    recommended_courses: list[str] = []
