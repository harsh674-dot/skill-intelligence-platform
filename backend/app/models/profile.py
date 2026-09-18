import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Float, Boolean, func, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class OfficialProfile(Base):
    __tablename__ = "official_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    designation: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    department: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    cadre: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    job_role_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="SET NULL"),
        nullable=True,
    )

    education: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    experience_years: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    prior_trainings: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    self_declared_competencies: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    profile_confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    data_source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="manual",
    )

    is_complete: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
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

    user = relationship(
        "User",
        back_populates="official_profile",
    )

    role = relationship(
        "Role",
        back_populates="official_profiles",
    )

    assessment_records = relationship(
        "CompetencyAssessmentRecord",
        back_populates="profile",
        cascade="all, delete-orphan",
    )

    learning_events = relationship(
        "LearningEvent",
        back_populates="profile",
        cascade="all, delete-orphan",
    )


class CompetencyAssessmentRecord(Base):
    __tablename__ = "competency_assessment_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("official_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    competency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competencies.id", ondelete="CASCADE"),
        nullable=False,
    )

    proficiency_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    proficiency_level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
    )

    assessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "proficiency_score >= 0 AND proficiency_score <= 100",
            name="check_proficiency_score",
        ),
        CheckConstraint(
            "proficiency_level BETWEEN 1 AND 5",
            name="check_proficiency_level",
        ),
    )

    profile = relationship(
        "OfficialProfile",
        back_populates="assessment_records",
    )

    competency = relationship(
        "Competency",
        back_populates="assessment_records",
    )


class LearningEvent(Base):
    __tablename__ = "learning_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("official_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )

    course_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="SET NULL"),
        nullable=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    external_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "event_type IN ('enrolment', 'completion', 'score', 'progress')",
            name="check_event_type",
        ),
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed', 'failed')",
            name="check_event_status",
        ),
    )

    profile = relationship(
        "OfficialProfile",
        back_populates="learning_events",
    )

    course = relationship(
        "Course",
        back_populates="learning_events",
    )
