import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class TPACRequest(Base):
    __tablename__ = "tpac_requests"

    id: Mapped[str] = mapped_column(
        String(50), 
        primary_key=True, 
        default=lambda: f"req-{uuid.uuid4().hex[:8]}"
    )
    course_id: Mapped[str] = mapped_column(String(50), nullable=False)
    requested_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id"), 
        nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    request_date: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False
    )
    approval_date: Mapped[datetime | None] = mapped_column(
        DateTime, 
        nullable=True
    )
    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id"), 
        nullable=True
    )
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
