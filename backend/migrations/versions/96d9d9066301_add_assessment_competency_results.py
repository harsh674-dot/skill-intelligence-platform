"""add assessment competency results

Revision ID: phase5_competency_results
Revises: 043e0a61f155
Create Date: 2026-09-10
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "phase5_competency_results"
down_revision: Union[str, Sequence[str], None] = "043e0a61f155"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "assessments",
        sa.Column(
            "competency_results",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "assessments",
        "competency_results",
    )