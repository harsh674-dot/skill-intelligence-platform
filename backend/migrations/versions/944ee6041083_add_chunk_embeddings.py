"""add chunk embeddings

Revision ID: 944ee6041083
Revises: e6db1c02ccdf
Create Date: 2026-09-09
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = "944ee6041083"
down_revision: Union[str, None] = "e6db1c02ccdf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "content_chunks",
        sa.Column(
            "embedding",
            Vector(1536),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "content_chunks",
        "embedding",
    )