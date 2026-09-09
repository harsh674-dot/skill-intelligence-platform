import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AIGeneratedQuestion(Base):
    __tablename__ = "ai_generated_questions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    learning_content_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "learning_content.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    competency_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "competencies.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    question_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="mcq",
    )

    difficulty: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="beginner",
    )

    options: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    correct_answer: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    source_chunk_ids: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    generation_model: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "question_type IN ('mcq')",
            name="check_ai_question_type",
        ),
        CheckConstraint(
            "difficulty IN ('beginner', 'intermediate', 'advanced')",
            name="check_ai_question_difficulty",
        ),
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')",
            name="check_ai_question_status",
        ),
    )

    learning_content = relationship(
        "LearningContent",
        back_populates="ai_generated_questions",
    )

    competency = relationship(
        "Competency",
        back_populates="ai_generated_questions",
    )