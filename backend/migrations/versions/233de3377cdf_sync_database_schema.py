"""sync database schema

Revision ID: 233de3377cdf
Revises: 0fde1c638df0
Create Date: 2026-09-10 00:21:53.933458

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "233de3377cdf"
down_revision: Union[str, Sequence[str], None] = "0fde1c638df0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ---------------------------------------------------------
    # AI GENERATED QUESTIONS
    # ---------------------------------------------------------

    op.alter_column(
        "ai_generated_questions",
        "question_type",
        existing_type=sa.VARCHAR(length=30),
        type_=sa.String(length=20),
        existing_nullable=False,
    )

    op.create_index(
        op.f("ix_ai_generated_questions_competency_id"),
        "ai_generated_questions",
        ["competency_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_ai_generated_questions_learning_content_id"),
        "ai_generated_questions",
        ["learning_content_id"],
        unique=False,
    )

    op.drop_constraint(
        op.f("ai_generated_questions_competency_id_fkey"),
        "ai_generated_questions",
        type_="foreignkey",
    )

    op.create_foreign_key(
        None,
        "ai_generated_questions",
        "competencies",
        ["competency_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # ---------------------------------------------------------
    # LEARNING CONTENT
    # ---------------------------------------------------------

    op.alter_column(
        "learning_content",
        "file_type",
        existing_type=sa.VARCHAR(length=50),
        type_=sa.String(length=20),
        existing_nullable=False,
    )

    op.alter_column(
        "learning_content",
        "source",
        existing_type=sa.VARCHAR(length=100),
        type_=sa.String(length=50),
        nullable=False,
    )

    # ---------------------------------------------------------
    # PROGRESS
    # ---------------------------------------------------------
    # Rename the existing column instead of dropping it.
    # This preserves all existing progress data.

    op.alter_column(
        "progress",
        "progress_percent",
        new_column_name="progress_percentage",
        existing_type=sa.SMALLINT(),
        existing_nullable=False,
    )

    op.drop_constraint(
        op.f("uq_user_course_progress"),
        "progress",
        type_="unique",
    )

    op.create_unique_constraint(
        "uq_progress_user_course",
        "progress",
        ["user_id", "course_id"],
    )

    op.drop_constraint(
        op.f("check_progress_percent"),
        "progress",
        type_="check",
    )

    op.create_check_constraint(
        "check_progress_percentage",
        "progress",
        "progress_percentage BETWEEN 0 AND 100",
    )

    op.create_check_constraint(
        "check_progress_status",
        "progress",
        "status IN ('not_started', 'in_progress', 'completed')",
    )

    # ---------------------------------------------------------
    # RECOMMENDATIONS
    # ---------------------------------------------------------

    op.add_column(
        "recommendations",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_unique_constraint(
        "uq_recommendation_user_course_competency",
        "recommendations",
        ["user_id", "course_id", "competency_id"],
    )

    op.create_check_constraint(
        "check_recommendation_status",
        "recommendations",
        "status IN ('pending', 'accepted', 'completed', 'dismissed')",
    )


def downgrade() -> None:
    """Downgrade schema."""

    # ---------------------------------------------------------
    # RECOMMENDATIONS
    # ---------------------------------------------------------

    op.drop_constraint(
        "check_recommendation_status",
        "recommendations",
        type_="check",
    )

    op.drop_constraint(
        "uq_recommendation_user_course_competency",
        "recommendations",
        type_="unique",
    )

    op.drop_column(
        "recommendations",
        "updated_at",
    )

    # ---------------------------------------------------------
    # PROGRESS
    # ---------------------------------------------------------

    op.drop_constraint(
        "check_progress_status",
        "progress",
        type_="check",
    )

    op.drop_constraint(
        "check_progress_percentage",
        "progress",
        type_="check",
    )

    op.alter_column(
        "progress",
        "progress_percentage",
        new_column_name="progress_percent",
        existing_type=sa.SMALLINT(),
        existing_nullable=False,
    )

    op.create_check_constraint(
        op.f("check_progress_percent"),
        "progress",
        "progress_percent >= 0 AND progress_percent <= 100",
    )

    op.drop_constraint(
        "uq_progress_user_course",
        "progress",
        type_="unique",
    )

    op.create_unique_constraint(
        op.f("uq_user_course_progress"),
        "progress",
        ["user_id", "course_id"],
        postgresql_nulls_not_distinct=False,
    )

    # ---------------------------------------------------------
    # LEARNING CONTENT
    # ---------------------------------------------------------

    op.alter_column(
        "learning_content",
        "source",
        existing_type=sa.String(length=50),
        type_=sa.VARCHAR(length=100),
        nullable=True,
    )

    op.alter_column(
        "learning_content",
        "file_type",
        existing_type=sa.String(length=20),
        type_=sa.VARCHAR(length=50),
        existing_nullable=False,
    )

    # ---------------------------------------------------------
    # AI GENERATED QUESTIONS
    # ---------------------------------------------------------

    op.drop_constraint(
        None,
        "ai_generated_questions",
        type_="foreignkey",
    )

    op.create_foreign_key(
        op.f("ai_generated_questions_competency_id_fkey"),
        "ai_generated_questions",
        "competencies",
        ["competency_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_index(
        op.f("ix_ai_generated_questions_learning_content_id"),
        table_name="ai_generated_questions",
    )

    op.drop_index(
        op.f("ix_ai_generated_questions_competency_id"),
        table_name="ai_generated_questions",
    )

    op.alter_column(
        "ai_generated_questions",
        "question_type",
        existing_type=sa.String(length=20),
        type_=sa.VARCHAR(length=30),
        existing_nullable=False,
    )