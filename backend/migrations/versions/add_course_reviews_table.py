"""add course reviews table

Revision ID: add_course_reviews_table
Revises: add_experience_reviews_table
Create Date: 2026-09-15
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "add_course_reviews_table"
down_revision: Union[str, Sequence[str], None] = "add_experience_reviews_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "course_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "course_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("courses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("helpfulness_rating", sa.Integer(), nullable=False),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "user_id",
            "course_id",
            name="uq_course_review_user_course",
        ),
        sa.CheckConstraint(
            "helpfulness_rating BETWEEN 1 AND 5",
            name="check_course_helpfulness_rating",
        ),
    )
    op.create_index("ix_course_reviews_user_id", "course_reviews", ["user_id"])
    op.create_index("ix_course_reviews_course_id", "course_reviews", ["course_id"])


def downgrade() -> None:
    op.drop_table("course_reviews")
