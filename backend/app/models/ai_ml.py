import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Float, Boolean, func, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CompetencyMapping(Base):
    __tablename__ = "competency_mappings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    competency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competencies.id", ondelete="CASCADE"),
        nullable=False,
    )

    mapping_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="rule_based",
    )

    model_version: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "mapping_type IN ('rule_based', 'ml_classifier', 'hybrid')",
            name="check_mapping_type",
        ),
        CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="check_mapping_confidence",
        ),
    )

    role = relationship(
        "Role",
        back_populates="competency_mappings",
    )

    competency = relationship(
        "Competency",
        back_populates="competency_mappings",
    )


class ModelGovernance(Base):
    __tablename__ = "model_governance"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    model_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    model_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    input_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    output_summary: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    latency_ms: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    is_approved: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    reviewed_by: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    review_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "model_type IN ('embedding', 'llm', 'classification', 'recommendation', 'assessment')",
            name="check_model_type",
        ),
    )
