"""add bloom_tag to ai_generated_questions and questions

Revision ID: add_bloom_tag
Revises: add_community_tables
Create Date: 2026-09-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "add_bloom_tag"
down_revision: Union[str, Sequence[str], None] = "add_course_reviews_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_BLOOM_CHECK = (
    "bloom_tag IS NULL OR bloom_tag IN "
    "('remember', 'understand', 'apply', 'analyze', 'evaluate', 'create')"
)

_TYPE_CHECK_AI = (
    "question_type IN ('mcq', 'true_false', 'fill_blank', 'short_answer')"
)


def upgrade() -> None:
    # ------------------------------------------------------------------
    # ai_generated_questions — add bloom_tag + widen question_type check
    # ------------------------------------------------------------------
    op.add_column(
        "ai_generated_questions",
        sa.Column(
            "bloom_tag",
            sa.String(length=30),
            nullable=True,
            comment=(
                "Bloom's Taxonomy cognitive level: "
                "remember | understand | apply | analyze | evaluate | create"
            ),
        ),
    )
    # Replace the restrictive question_type constraint with the wider one
    op.drop_constraint(
        "check_ai_question_type",
        "ai_generated_questions",
        type_="check",
    )
    op.create_check_constraint(
        "check_ai_question_type",
        "ai_generated_questions",
        _TYPE_CHECK_AI,
    )
    op.create_check_constraint(
        "check_ai_question_bloom_tag",
        "ai_generated_questions",
        _BLOOM_CHECK,
    )

    # ------------------------------------------------------------------
    # questions — add bloom_tag
    # ------------------------------------------------------------------
    op.add_column(
        "questions",
        sa.Column(
            "bloom_tag",
            sa.String(length=30),
            nullable=True,
            comment=(
                "Bloom's Taxonomy cognitive level: "
                "remember | understand | apply | analyze | evaluate | create"
            ),
        ),
    )
    op.create_check_constraint(
        "check_question_bloom_tag",
        "questions",
        _BLOOM_CHECK,
    )


def downgrade() -> None:
    op.drop_constraint("check_question_bloom_tag", "questions", type_="check")
    op.drop_column("questions", "bloom_tag")

    op.drop_constraint("check_ai_question_bloom_tag", "ai_generated_questions", type_="check")
    op.drop_constraint("check_ai_question_type", "ai_generated_questions", type_="check")
    op.create_check_constraint(
        "check_ai_question_type",
        "ai_generated_questions",
        "question_type IN ('mcq')",
    )
    op.drop_column("ai_generated_questions", "bloom_tag")
