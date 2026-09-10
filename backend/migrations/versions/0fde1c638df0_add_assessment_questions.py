"""add assessment questions

Revision ID: 0fde1c638df0
Revises: 88c94e0215d0
Create Date: 2026-09-10 00:06:07.004970

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0fde1c638df0"
down_revision: Union[str, Sequence[str], None] = "88c94e0215d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create assessment_questions table."""

    op.create_table(
        "assessment_questions",
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "assessment_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "question_id",
            sa.UUID(),
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
        sa.UniqueConstraint(
            "assessment_id",
            "question_id",
            name="uq_assessment_question",
        ),
    )


def downgrade() -> None:
    """Drop assessment_questions table."""

    op.drop_table("assessment_questions")