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


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    provider: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    external_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    duration_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    level: Mapped[str | None] = mapped_column(
        String(30),
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

    competencies = relationship(
        "CourseCompetency",
        back_populates="course",
        cascade="all, delete-orphan",
    )

    recommendations = relationship(
        "Recommendation",
        back_populates="course",
    )

    progress = relationship(
        "Progress",
        back_populates="course",
        cascade="all, delete-orphan",
    )


class CourseCompetency(Base):
    __tablename__ = "course_competencies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )

    competency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competencies.id", ondelete="CASCADE"),
        nullable=False,
    )

    target_level: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "course_id",
            "competency_id",
            name="uq_course_competency",
        ),
        CheckConstraint(
            "target_level BETWEEN 1 AND 5",
            name="check_target_level",
        ),
    )

    course = relationship(
        "Course",
        back_populates="competencies",
    )

    competency = relationship(
        "Competency",
        back_populates="course_competencies",
    )