"""change embeddings to 384 dimensions

Revision ID: 09769b8e6dc7
Revises: 6f7d81fd655a
Create Date: 2026-09-09
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = "09769b8e6dc7"
down_revision: Union[str, None] = "6f7d81fd655a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Existing embeddings, if any, cannot be converted from
    # 1536 dimensions to 384 dimensions.
    #
    # Currently your uploaded chunks do not have embeddings,
    # so it is safe to clear them before changing the dimension.

    op.execute(
        """
        UPDATE content_chunks
        SET embedding = NULL
        WHERE embedding IS NOT NULL
        """
    )

    op.execute(
        """
        ALTER TABLE content_chunks
        ALTER COLUMN embedding TYPE vector(384)
        """
    )


def downgrade() -> None:
    # Clear 384-dimensional embeddings before reverting.
    op.execute(
        """
        UPDATE content_chunks
        SET embedding = NULL
        WHERE embedding IS NOT NULL
        """
    )

    op.execute(
        """
        ALTER TABLE content_chunks
        ALTER COLUMN embedding TYPE vector(1536)
        """
    )