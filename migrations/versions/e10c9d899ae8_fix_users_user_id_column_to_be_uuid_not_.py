"""fix users user_id column to be uuid not integer

The `users.user_id` column was live in the database as a plain SERIAL
integer, even though the model (and the original create-table migration
script) declare it as UUID. Both tables that reference it were empty, so
this converts all three columns to UUID with no data-loss risk.

Revision ID: e10c9d899ae8
Revises: 897d284b1c03
Create Date: 2026-08-04 16:32:15.087129

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e10c9d899ae8'
down_revision: Union[str, Sequence[str], None] = '897d284b1c03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint('booking_item_returned_by_id_fkey', 'booking_item', type_='foreignkey')
    op.drop_constraint('bookings_user_id_fkey', 'bookings', type_='foreignkey')

    op.execute("ALTER TABLE users ALTER COLUMN user_id DROP DEFAULT")
    op.execute("ALTER TABLE users ALTER COLUMN user_id TYPE uuid USING gen_random_uuid()")
    op.execute("DROP SEQUENCE IF EXISTS users_user_id_seq")

    op.execute("ALTER TABLE bookings ALTER COLUMN user_id TYPE uuid USING gen_random_uuid()")
    op.execute("ALTER TABLE booking_item ALTER COLUMN returned_by_id TYPE uuid USING gen_random_uuid()")

    op.create_foreign_key(
        'bookings_user_id_fkey', 'bookings', 'users', ['user_id'], ['user_id']
    )
    op.create_foreign_key(
        'booking_item_returned_by_id_fkey', 'booking_item', 'users', ['returned_by_id'], ['user_id']
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('booking_item_returned_by_id_fkey', 'booking_item', type_='foreignkey')
    op.drop_constraint('bookings_user_id_fkey', 'bookings', type_='foreignkey')

    op.execute("ALTER TABLE booking_item ALTER COLUMN returned_by_id TYPE integer USING NULL")
    op.execute("ALTER TABLE bookings ALTER COLUMN user_id TYPE integer USING NULL")

    op.execute("CREATE SEQUENCE IF NOT EXISTS users_user_id_seq")
    op.execute("ALTER TABLE users ALTER COLUMN user_id TYPE integer USING NULL")
    op.execute("ALTER TABLE users ALTER COLUMN user_id SET DEFAULT nextval('users_user_id_seq')")
    op.execute("ALTER SEQUENCE users_user_id_seq OWNED BY users.user_id")

    op.create_foreign_key(
        'bookings_user_id_fkey', 'bookings', 'users', ['user_id'], ['user_id']
    )
    op.create_foreign_key(
        'booking_item_returned_by_id_fkey', 'booking_item', 'users', ['returned_by_id'], ['user_id']
    )
