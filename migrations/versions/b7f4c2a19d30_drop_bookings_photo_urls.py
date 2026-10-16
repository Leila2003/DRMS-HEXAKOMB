"""drop bookings.photo_urls

Booking photos are no longer captured. This drops the now-unused
`photo_urls` array column from `bookings`, matching the model/schema/
service changes (the booking-photo upload path is removed entirely).

Revision ID: b7f4c2a19d30
Revises: 1e2de1f455b9
Create Date: 2026-09-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'b7f4c2a19d30'
down_revision: Union[str, Sequence[str], None] = '1e2de1f455b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('bookings', 'photo_urls')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        'bookings',
        sa.Column(
            'photo_urls',
            postgresql.ARRAY(sa.String(length=500)),
            server_default=sa.text("'{}'"),
            nullable=False,
        ),
    )
    # Note: values aren't restored — the column was dropped, not just hidden.
