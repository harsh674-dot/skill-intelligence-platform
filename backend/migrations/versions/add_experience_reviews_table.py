"""add experience reviews table

Revision ID: add_experience_reviews_table
Revises: add_community_tables
Create Date: 2026-09-15
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "add_experience_reviews_table"
down_revision: Union[str, Sequence[str], None] = "add_community_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "experience_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "category IN ('platform', 'training_program', 'onboarding')",
            name="check_experience_review_category",
        ),
        sa.CheckConstraint(
            "rating BETWEEN 1 AND 5",
            name="check_experience_review_rating",
        ),
    )
    op.create_index("ix_experience_reviews_user_id", "experience_reviews", ["user_id"])
    op.create_index("ix_experience_reviews_category", "experience_reviews", ["category"])


def downgrade() -> None:
    op.drop_table("experience_reviews")
