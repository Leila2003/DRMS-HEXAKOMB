"""add is_deleted flag

Revision ID: d6173e26cd44
Revises: a11f6540ec60
Create Date: 2026-07-31 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd6173e26cd44'
down_revision: Union[str, Sequence[str], None] = 'a11f6540ec60'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLES = ['customers', 'items_category', 'users', 'bookings', 'booking_item']


def upgrade() -> None:
    """Upgrade schema."""
    for table in TABLES:
        op.add_column(
            table,
            sa.Column('is_deleted', sa.Boolean(), server_default=sa.false(), nullable=False),
        )


def downgrade() -> None:
    """Downgrade schema."""
    for table in TABLES:
        op.drop_column(table, 'is_deleted')
