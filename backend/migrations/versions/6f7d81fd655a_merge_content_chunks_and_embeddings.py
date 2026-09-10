"""merge content chunks and embeddings

Revision ID: 6f7d81fd655a
Revises: 6c128463c365, 944ee6041083
Create Date: 2026-09-09 01:34:37.461679

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f7d81fd655a'
down_revision: Union[str, Sequence[str], None] = ('6c128463c365', '944ee6041083')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
