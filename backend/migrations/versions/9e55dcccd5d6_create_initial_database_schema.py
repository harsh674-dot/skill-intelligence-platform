"""create initial database schema

Revision ID: 9e55dcccd5d6
Revises:
Create Date: 2026-09-04 13:30:14.672253

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "9e55dcccd5d6"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the initial database schema."""

    # -------------------------------------------------------------------------
    # COMPETENCIES
    # -------------------------------------------------------------------------

    op.create_table(
        "competencies",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("domain", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # -------------------------------------------------------------------------
    # COURSES
    # -------------------------------------------------------------------------

    op.create_table(
        "courses",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("provider", sa.String(length=150), nullable=True),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("level", sa.String(length=30), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # -------------------------------------------------------------------------
    # ROLES
    # -------------------------------------------------------------------------

    op.create_table(
        "roles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # -------------------------------------------------------------------------
    # USERS
    # -------------------------------------------------------------------------

    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("access_role", sa.String(length=20), nullable=False),
        sa.Column("designation", sa.String(length=150), nullable=True),
        sa.Column("department", sa.String(length=150), nullable=True),
        sa.Column("job_role_id", sa.UUID(), nullable=True),
        sa.Column("education", sa.Text(), nullable=True),
        sa.Column("experience_years", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "access_role IN ('employee', 'admin')",
            name="check_user_access_role",
        ),
        sa.CheckConstraint(
            "experience_years >= 0",
            name="check_experience_years",
        ),
        sa.ForeignKeyConstraint(
            ["job_role_id"],
            ["roles.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_users_email"),
        "users",
        ["email"],
        unique=True,
    )

    # -------------------------------------------------------------------------
    # ASSESSMENTS
    # -------------------------------------------------------------------------

    op.create_table(
        "assessments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("assessment_type", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "score",
            sa.Numeric(precision=5, scale=2),
            nullable=True,
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.CheckConstraint(
            "assessment_type IN ('initial', 'learning', 'reassessment')",
            name="check_assessment_type",
        ),
        sa.CheckConstraint(
            "status IN ('in_progress', 'completed', 'abandoned')",
            name="check_assessment_status",
        ),
        sa.CheckConstraint(
            "score IS NULL OR (score >= 0 AND score <= 100)",
            name="check_assessment_score",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # -------------------------------------------------------------------------
    # COURSE COMPETENCIES
    # -------------------------------------------------------------------------

    op.create_table(
        "course_competencies",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("course_id", sa.UUID(), nullable=False),
        sa.Column("competency_id", sa.UUID(), nullable=False),
        sa.Column("target_level", sa.SmallInteger(), nullable=False),
        sa.CheckConstraint(
            "target_level BETWEEN 1 AND 5",
            name="check_target_level",
        ),
        sa.ForeignKeyConstraint(
            ["competency_id"],
            ["competencies.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["courses.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "course_id",
            "competency_id",
            name="uq_course_competency",
        ),
    )

    # -------------------------------------------------------------------------
    # LEARNING CONTENT
    # -------------------------------------------------------------------------

    op.create_table(
        "learning_content",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_type", sa.String(length=50), nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column("uploaded_by", sa.UUID(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('uploaded', 'processing', 'ready', 'failed', 'archived')",
            name="check_learning_content_status",
        ),
        sa.ForeignKeyConstraint(
            ["uploaded_by"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # -------------------------------------------------------------------------
    # PROGRESS
    # -------------------------------------------------------------------------

    op.create_table(
        "progress",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("course_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "progress_percent",
            sa.SmallInteger(),
            nullable=False,
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "progress_percent BETWEEN 0 AND 100",
            name="check_progress_percent",
        ),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["courses.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "course_id",
            name="uq_user_course_progress",
        ),
    )

    # -------------------------------------------------------------------------
    # RECOMMENDATIONS
    # -------------------------------------------------------------------------

    op.create_table(
        "recommendations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("course_id", sa.UUID(), nullable=False),
        sa.Column("competency_id", sa.UUID(), nullable=False),
        sa.Column(
            "gap_score",
            sa.Numeric(precision=5, scale=2),
            nullable=False,
        ),
        sa.Column(
            "priority_score",
            sa.Numeric(precision=5, scale=2),
            nullable=False,
        ),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["competency_id"],
            ["competencies.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["courses.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # -------------------------------------------------------------------------
    # ROLE COMPETENCIES
    # -------------------------------------------------------------------------

    op.create_table(
        "role_competencies",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("role_id", sa.UUID(), nullable=False),
        sa.Column("competency_id", sa.UUID(), nullable=False),
        sa.Column("required_level", sa.SmallInteger(), nullable=False),
        sa.Column("is_critical", sa.Boolean(), nullable=False),
        sa.CheckConstraint(
            "required_level BETWEEN 1 AND 5",
            name="check_required_level",
        ),
        sa.ForeignKeyConstraint(
            ["competency_id"],
            ["competencies.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "role_id",
            "competency_id",
            name="uq_role_competency",
        ),
    )

    # -------------------------------------------------------------------------
    # USER COMPETENCIES
    # -------------------------------------------------------------------------

    op.create_table(
        "user_competencies",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("competency_id", sa.UUID(), nullable=False),
        sa.Column("current_level", sa.SmallInteger(), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column(
            "last_assessed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "current_level BETWEEN 1 AND 5",
            name="check_current_level",
        ),
        sa.ForeignKeyConstraint(
            ["competency_id"],
            ["competencies.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "competency_id",
            name="uq_user_competency",
        ),
    )

    # -------------------------------------------------------------------------
    # QUESTIONS
    # -------------------------------------------------------------------------

    op.create_table(
        "questions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("competency_id", sa.UUID(), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(length=30), nullable=False),
        sa.Column("difficulty", sa.String(length=20), nullable=False),
        sa.Column(
            "options",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "correct_answer",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("source_content_id", sa.UUID(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "difficulty IN ('beginner', 'intermediate', 'advanced')",
            name="check_question_difficulty",
        ),
        sa.ForeignKeyConstraint(
            ["competency_id"],
            ["competencies.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["source_content_id"],
            ["learning_content.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # -------------------------------------------------------------------------
    # ANSWERS
    # -------------------------------------------------------------------------

    op.create_table(
        "answers",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("assessment_id", sa.UUID(), nullable=False),
        sa.Column("question_id", sa.UUID(), nullable=False),
        sa.Column(
            "selected_answer",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column(
            "answered_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["assessment_id"],
            ["assessments.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["questions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        comment="Stores one response per question per assessment",
    )


def downgrade() -> None:
    """Drop the initial database schema."""

    op.drop_table("answers")
    op.drop_table("questions")
    op.drop_table("user_competencies")
    op.drop_table("role_competencies")
    op.drop_table("recommendations")
    op.drop_table("progress")
    op.drop_table("learning_content")
    op.drop_table("course_competencies")
    op.drop_table("assessments")
    op.drop_index(
        op.f("ix_users_email"),
        table_name="users",
    )
    op.drop_table("users")
    op.drop_table("roles")
    op.drop_table("courses")
    op.drop_table("competencies")