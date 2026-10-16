"""convert business-entity PKs to UUID and merge booking photos into bookings

Converts customers.customer_id, items_category.category_id,
bookings.booking_id, booking_item.booking_item_id, and
notifications.notification_id — plus every FK pointing at them — from
Integer to UUID, extending the convention already used for
users.user_id (e10c9d899ae8) to every entity. Unlike that migration,
this one preserves existing relationships even if the tables aren't
empty: a UUID is generated once per row and propagated to every FK
that referenced it, via a join on the old integer id, before any
integer column is dropped.

Also folds booking_photos into a new `photo_urls` array column on
bookings — a booking can still hold any number of photos (appended to
on each upload), they're just no longer a separate table/model.

Revision ID: ca13461ca7df
Revises: f3a1c9d2b4e7
Create Date: 2026-08-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'ca13461ca7df'
down_revision: Union[str, Sequence[str], None] = 'f3a1c9d2b4e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # --- 1. Fold booking_photos into bookings.photo_urls while
    # bookings.booking_id is still the original integer, so the join is trivial.
    op.add_column('bookings', sa.Column('photo_urls', postgresql.ARRAY(sa.String(length=500)), nullable=True))
    op.execute(
        """
        UPDATE bookings b
        SET photo_urls = sub.urls
        FROM (
            SELECT booking_id, array_agg(image_url ORDER BY created_at) AS urls
            FROM booking_photos
            WHERE is_deleted = false
            GROUP BY booking_id
        ) sub
        WHERE b.booking_id = sub.booking_id
        """
    )
    op.execute("UPDATE bookings SET photo_urls = '{}' WHERE photo_urls IS NULL")
    op.execute("ALTER TABLE bookings ALTER COLUMN photo_urls SET DEFAULT '{}'")
    op.execute("ALTER TABLE bookings ALTER COLUMN photo_urls SET NOT NULL")

    op.drop_index(op.f('ix_booking_photos_photo_id'), table_name='booking_photos')
    op.drop_index(op.f('ix_booking_photos_booking_id'), table_name='booking_photos')
    op.drop_table('booking_photos')

    # --- 2. Add new UUID columns everywhere a PK/FK needs to move to UUID,
    # leaving the old integer columns in place until every new column is
    # populated and joins can still resolve against them.
    op.add_column('customers', sa.Column('customer_id_new', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('items_category', sa.Column('category_id_new', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('bookings', sa.Column('booking_id_new', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('bookings', sa.Column('customer_id_new', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('booking_item', sa.Column('booking_item_id_new', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('booking_item', sa.Column('booking_id_new', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('booking_item', sa.Column('category_id_new', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('notifications', sa.Column('notification_id_new', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('notifications', sa.Column('booking_id_new', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('notifications', sa.Column('category_id_new', postgresql.UUID(as_uuid=True), nullable=True))

    # --- 3. Generate a fresh UUID per row for every PK.
    op.execute("UPDATE customers SET customer_id_new = gen_random_uuid()")
    op.execute("UPDATE items_category SET category_id_new = gen_random_uuid()")
    op.execute("UPDATE bookings SET booking_id_new = gen_random_uuid()")
    op.execute("UPDATE booking_item SET booking_item_id_new = gen_random_uuid()")
    op.execute("UPDATE notifications SET notification_id_new = gen_random_uuid()")

    # --- 4. Propagate those new UUIDs to every FK, joined on the
    # still-intact old integer ids, so every relationship survives the swap.
    op.execute(
        """
        UPDATE bookings b SET customer_id_new = c.customer_id_new
        FROM customers c WHERE c.customer_id = b.customer_id
        """
    )
    op.execute(
        """
        UPDATE booking_item bi SET booking_id_new = b.booking_id_new
        FROM bookings b WHERE b.booking_id = bi.booking_id
        """
    )
    op.execute(
        """
        UPDATE booking_item bi SET category_id_new = ic.category_id_new
        FROM items_category ic WHERE ic.category_id = bi.category_id
        """
    )
    op.execute(
        """
        UPDATE notifications n SET booking_id_new = b.booking_id_new
        FROM bookings b WHERE b.booking_id = n.booking_id
        """
    )
    op.execute(
        """
        UPDATE notifications n SET category_id_new = ic.category_id_new
        FROM items_category ic WHERE ic.category_id = n.category_id
        """
    )

    # --- 5. Lock down NOT NULL to match the columns being replaced.
    # notifications.booking_id_new / category_id_new stay nullable, matching
    # the optional link columns they replace.
    for table, column in [
        ('customers', 'customer_id_new'),
        ('items_category', 'category_id_new'),
        ('bookings', 'booking_id_new'),
        ('bookings', 'customer_id_new'),
        ('booking_item', 'booking_item_id_new'),
        ('booking_item', 'booking_id_new'),
        ('booking_item', 'category_id_new'),
        ('notifications', 'notification_id_new'),
    ]:
        op.execute(f"ALTER TABLE {table} ALTER COLUMN {column} SET NOT NULL")

    # --- 6. Drop old FKs/PKs/indexes, drop the old integer columns, rename
    # the new UUID columns into place, then rebuild PKs/FKs/indexes.
    op.drop_constraint('bookings_customer_id_fkey', 'bookings', type_='foreignkey')
    op.drop_constraint('booking_item_booking_id_fkey', 'booking_item', type_='foreignkey')
    op.drop_constraint('booking_item_category_id_fkey', 'booking_item', type_='foreignkey')
    op.drop_constraint('notifications_booking_id_fkey', 'notifications', type_='foreignkey')
    op.drop_constraint('notifications_category_id_fkey', 'notifications', type_='foreignkey')

    op.drop_constraint('bookings_pkey', 'bookings', type_='primary')
    op.drop_constraint('booking_item_pkey', 'booking_item', type_='primary')
    op.drop_constraint('customers_pkey', 'customers', type_='primary')
    op.drop_constraint('items_category_pkey', 'items_category', type_='primary')
    op.drop_constraint('notifications_pkey', 'notifications', type_='primary')

    for table, ix in [
        ('customers', 'ix_customers_customer_id'),
        ('items_category', 'ix_items_category_category_id'),
        ('bookings', 'ix_bookings_booking_id'),
        ('bookings', 'ix_bookings_customer_id'),
        ('booking_item', 'ix_booking_item_booking_item_id'),
        ('booking_item', 'ix_booking_item_booking_id'),
        ('booking_item', 'ix_booking_item_category_id'),
        ('notifications', 'ix_notifications_notification_id'),
        ('notifications', 'ix_notifications_booking_id'),
        ('notifications', 'ix_notifications_category_id'),
    ]:
        op.drop_index(op.f(ix), table_name=table)

    op.drop_column('customers', 'customer_id')
    op.drop_column('items_category', 'category_id')
    op.drop_column('bookings', 'booking_id')
    op.drop_column('bookings', 'customer_id')
    op.drop_column('booking_item', 'booking_item_id')
    op.drop_column('booking_item', 'booking_id')
    op.drop_column('booking_item', 'category_id')
    op.drop_column('notifications', 'notification_id')
    op.drop_column('notifications', 'booking_id')
    op.drop_column('notifications', 'category_id')

    for table, old, new in [
        ('customers', 'customer_id_new', 'customer_id'),
        ('items_category', 'category_id_new', 'category_id'),
        ('bookings', 'booking_id_new', 'booking_id'),
        ('bookings', 'customer_id_new', 'customer_id'),
        ('booking_item', 'booking_item_id_new', 'booking_item_id'),
        ('booking_item', 'booking_id_new', 'booking_id'),
        ('booking_item', 'category_id_new', 'category_id'),
        ('notifications', 'notification_id_new', 'notification_id'),
        ('notifications', 'booking_id_new', 'booking_id'),
        ('notifications', 'category_id_new', 'category_id'),
    ]:
        op.execute(f"ALTER TABLE {table} RENAME COLUMN {old} TO {new}")

    op.create_primary_key('customers_pkey', 'customers', ['customer_id'])
    op.create_primary_key('items_category_pkey', 'items_category', ['category_id'])
    op.create_primary_key('bookings_pkey', 'bookings', ['booking_id'])
    op.create_primary_key('booking_item_pkey', 'booking_item', ['booking_item_id'])
    op.create_primary_key('notifications_pkey', 'notifications', ['notification_id'])

    op.create_foreign_key('bookings_customer_id_fkey', 'bookings', 'customers', ['customer_id'], ['customer_id'])
    op.create_foreign_key('booking_item_booking_id_fkey', 'booking_item', 'bookings', ['booking_id'], ['booking_id'])
    op.create_foreign_key('booking_item_category_id_fkey', 'booking_item', 'items_category', ['category_id'], ['category_id'])
    op.create_foreign_key('notifications_booking_id_fkey', 'notifications', 'bookings', ['booking_id'], ['booking_id'])
    op.create_foreign_key('notifications_category_id_fkey', 'notifications', 'items_category', ['category_id'], ['category_id'])

    op.create_index(op.f('ix_customers_customer_id'), 'customers', ['customer_id'], unique=False)
    op.create_index(op.f('ix_items_category_category_id'), 'items_category', ['category_id'], unique=False)
    op.create_index(op.f('ix_bookings_booking_id'), 'bookings', ['booking_id'], unique=False)
    op.create_index(op.f('ix_bookings_customer_id'), 'bookings', ['customer_id'], unique=False)
    op.create_index(op.f('ix_booking_item_booking_item_id'), 'booking_item', ['booking_item_id'], unique=False)
    op.create_index(op.f('ix_booking_item_booking_id'), 'booking_item', ['booking_id'], unique=False)
    op.create_index(op.f('ix_booking_item_category_id'), 'booking_item', ['category_id'], unique=False)
    op.create_index(op.f('ix_notifications_notification_id'), 'notifications', ['notification_id'], unique=False)
    op.create_index(op.f('ix_notifications_booking_id'), 'notifications', ['booking_id'], unique=False)
    op.create_index(op.f('ix_notifications_category_id'), 'notifications', ['category_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema.

    Best-effort and lossy, matching the precedent set by e10c9d899ae8 for
    the users.user_id conversion: UUID -> integer has no faithful inverse
    (there's no original sequence to restore), so FK columns are reset to
    NULL and PK columns get fresh sequence-backed integers rather than
    their original values.
    """
    op.drop_constraint('bookings_customer_id_fkey', 'bookings', type_='foreignkey')
    op.drop_constraint('booking_item_booking_id_fkey', 'booking_item', type_='foreignkey')
    op.drop_constraint('booking_item_category_id_fkey', 'booking_item', type_='foreignkey')
    op.drop_constraint('notifications_booking_id_fkey', 'notifications', type_='foreignkey')
    op.drop_constraint('notifications_category_id_fkey', 'notifications', type_='foreignkey')

    op.execute("ALTER TABLE notifications ALTER COLUMN category_id TYPE integer USING NULL")
    op.execute("ALTER TABLE notifications ALTER COLUMN booking_id TYPE integer USING NULL")
    op.execute("CREATE SEQUENCE IF NOT EXISTS notifications_notification_id_seq")
    op.execute("ALTER TABLE notifications ALTER COLUMN notification_id TYPE integer USING NULL")
    op.execute("ALTER TABLE notifications ALTER COLUMN notification_id SET DEFAULT nextval('notifications_notification_id_seq')")
    op.execute("ALTER SEQUENCE notifications_notification_id_seq OWNED BY notifications.notification_id")

    op.execute("ALTER TABLE booking_item ALTER COLUMN category_id TYPE integer USING NULL")
    op.execute("ALTER TABLE booking_item ALTER COLUMN booking_id TYPE integer USING NULL")
    op.execute("CREATE SEQUENCE IF NOT EXISTS booking_item_booking_item_id_seq")
    op.execute("ALTER TABLE booking_item ALTER COLUMN booking_item_id TYPE integer USING NULL")
    op.execute("ALTER TABLE booking_item ALTER COLUMN booking_item_id SET DEFAULT nextval('booking_item_booking_item_id_seq')")
    op.execute("ALTER SEQUENCE booking_item_booking_item_id_seq OWNED BY booking_item.booking_item_id")

    op.execute("ALTER TABLE bookings ALTER COLUMN customer_id TYPE integer USING NULL")
    op.execute("CREATE SEQUENCE IF NOT EXISTS bookings_booking_id_seq")
    op.execute("ALTER TABLE bookings ALTER COLUMN booking_id TYPE integer USING NULL")
    op.execute("ALTER TABLE bookings ALTER COLUMN booking_id SET DEFAULT nextval('bookings_booking_id_seq')")
    op.execute("ALTER SEQUENCE bookings_booking_id_seq OWNED BY bookings.booking_id")

    op.execute("CREATE SEQUENCE IF NOT EXISTS items_category_category_id_seq")
    op.execute("ALTER TABLE items_category ALTER COLUMN category_id TYPE integer USING NULL")
    op.execute("ALTER TABLE items_category ALTER COLUMN category_id SET DEFAULT nextval('items_category_category_id_seq')")
    op.execute("ALTER SEQUENCE items_category_category_id_seq OWNED BY items_category.category_id")

    op.execute("CREATE SEQUENCE IF NOT EXISTS customers_customer_id_seq")
    op.execute("ALTER TABLE customers ALTER COLUMN customer_id TYPE integer USING NULL")
    op.execute("ALTER TABLE customers ALTER COLUMN customer_id SET DEFAULT nextval('customers_customer_id_seq')")
    op.execute("ALTER SEQUENCE customers_customer_id_seq OWNED BY customers.customer_id")

    op.create_foreign_key('bookings_customer_id_fkey', 'bookings', 'customers', ['customer_id'], ['customer_id'])
    op.create_foreign_key('booking_item_booking_id_fkey', 'booking_item', 'bookings', ['booking_id'], ['booking_id'])
    op.create_foreign_key('booking_item_category_id_fkey', 'booking_item', 'items_category', ['category_id'], ['category_id'])
    op.create_foreign_key('notifications_booking_id_fkey', 'notifications', 'bookings', ['booking_id'], ['booking_id'])
    op.create_foreign_key('notifications_category_id_fkey', 'notifications', 'items_category', ['category_id'], ['category_id'])

    op.drop_column('bookings', 'photo_urls')

    op.create_table(
        'booking_photos',
        sa.Column('photo_id', sa.Integer(), nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.booking_id'], ),
        sa.PrimaryKeyConstraint('photo_id'),
    )
    op.create_index(op.f('ix_booking_photos_booking_id'), 'booking_photos', ['booking_id'], unique=False)
    op.create_index(op.f('ix_booking_photos_photo_id'), 'booking_photos', ['photo_id'], unique=False)
