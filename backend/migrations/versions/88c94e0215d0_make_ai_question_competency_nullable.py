"""make ai question competency nullable

Revision ID: 88c94e0215d0
Revises: 09769b8e6dc7
Create Date: 2026-09-09 02:38:00.131748

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "88c94e0215d0"
down_revision: Union[str, Sequence[str], None] = "09769b8e6dc7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "ai_generated_questions",
        "competency_id",
        existing_type=postgresql.UUID(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "ai_generated_questions",
        "competency_id",
        existing_type=postgresql.UUID(),
        nullable=False,
    )