"""rename national_id_url to national_id_photo

Revision ID: 50168049b897
Revises: d6173e26cd44
Create Date: 2026-07-31 15:27:22.448613

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50168049b897'
down_revision: Union[str, Sequence[str], None] = 'd6173e26cd44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("customers", "national_id_url", new_column_name="national_id_photo")


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("customers", "national_id_photo", new_column_name="national_id_url")
