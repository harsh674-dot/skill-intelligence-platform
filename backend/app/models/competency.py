import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Competency(Base):
    __tablename__ = "competencies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
    )

    domain: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
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

    role_competencies = relationship(
        "RoleCompetency",
        back_populates="competency",
        cascade="all, delete-orphan",
    )

    user_competencies = relationship(
        "UserCompetency",
        back_populates="competency",
        cascade="all, delete-orphan",
    )

    # Existing manually created question bank
    questions = relationship(
        "Question",
        back_populates="competency",
    )

    # AI-generated questions from uploaded learning content
    ai_generated_questions = relationship(
        "AIGeneratedQuestion",
        back_populates="competency",
        cascade="all, delete-orphan",
    )

    course_competencies = relationship(
        "CourseCompetency",
        back_populates="competency",
        cascade="all, delete-orphan",
    )
    recommendations = relationship(
        "Recommendation",
        back_populates="competency",
        cascade="all, delete-orphan",
    )


class RoleCompetency(Base):
    __tablename__ = "role_competencies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
    )

    competency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competencies.id", ondelete="CASCADE"),
        nullable=False,
    )

    required_level: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    is_critical: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    organizational_priority: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=1,
    )

    __table_args__ = (
        UniqueConstraint(
            "role_id",
            "competency_id",
            name="uq_role_competency",
        ),
        CheckConstraint(
            "required_level BETWEEN 1 AND 5",
            name="check_required_level",
        ),
        CheckConstraint(
            "organizational_priority BETWEEN 1 AND 3",
            name="check_organizational_priority",
        ),
    )

    role = relationship(
        "Role",
        back_populates="role_competencies",
    )

    competency = relationship(
        "Competency",
        back_populates="role_competencies",
    )


class UserCompetency(Base):
    __tablename__ = "user_competencies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    competency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competencies.id", ondelete="CASCADE"),
        nullable=False,
    )

    current_level: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    last_assessed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "competency_id",
            name="uq_user_competency",
        ),
        CheckConstraint(
            "current_level BETWEEN 1 AND 5",
            name="check_current_level",
        ),
    )

    user = relationship(
        "User",
        back_populates="user_competencies",
    )

    competency = relationship(
        "Competency",
        back_populates="user_competencies",
    )