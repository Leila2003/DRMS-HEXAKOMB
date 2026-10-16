"""introduce businesses and scope users/customers/bookings/categories/notifications to a business

Adds multi-tenant support: a `businesses` table, `users.business_id` +
new `SUPER_ADMIN`/`BUSINESS_ADMIN` role labels, and `business_id` on
`customers`, `items_category`, `bookings`, `notifications` so each
business's data is isolated from every other business's. Also swaps
the previously-global unique constraints on `customers.contact` and
`items_category.item_name` for per-business ones, so two different
shops can each have a customer with the same phone number or a
category with the same name.

Data migration for the existing single-tenant install:
  - The original admin account (role ADMIN) becomes the platform
    SUPER_ADMIN, detached from any business.
  - A new Business + BUSINESS_ADMIN owner account is created for the
    shop that account used to run day-to-day.
  - All existing staff/customers/bookings/categories/notifications are
    attached to that one business.

The new owner account is a placeholder — rename it and change its
password immediately after this migration runs:
    email:    owner@hexakomb.com
    password: ChangeMe@2026

Revision ID: c1e038d21aaf
Revises: ca13461ca7df
Create Date: 2026-08-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c1e038d21aaf'
down_revision: Union[str, Sequence[str], None] = 'ca13461ca7df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


BUSINESS_ID = '5e70d439-bf78-475b-90b1-8457695641ad'
OWNER_USER_ID = '940d08f1-9a4a-41ea-b61b-561b1efb3302'
OWNER_PASSWORD_HASH = '$2b$12$LWzRqPfMGqnSgITY9zt7M.HCO2LYAIv/K6v3e9phUceo91qIPUMH6'  # "ChangeMe@2026"
ORIGINAL_ADMIN_EMAIL = 'leilamugeni@gmail.com'

BUSINESS_SCOPED_TABLES = ('customers', 'items_category', 'bookings', 'notifications')


def upgrade() -> None:
    """Upgrade schema."""

    # --- 1. New enum labels. Must run outside this migration's transaction —
    # Postgres won't let a label be used in the same transaction it was added in.
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'SUPER_ADMIN'")
        op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'BUSINESS_ADMIN'")

    # --- 2. businesses table
    op.create_table(
        'businesses',
        sa.Column('business_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    )
    op.create_index('ix_businesses_business_id', 'businesses', ['business_id'])
    op.create_index('ix_businesses_email', 'businesses', ['email'], unique=True)

    # --- 3. users.business_id
    op.add_column('users', sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index('ix_users_business_id', 'users', ['business_id'])
    op.create_foreign_key(
        'users_business_id_fkey', 'users', 'businesses', ['business_id'], ['business_id']
    )

    # --- 4. business_id on the rest of the business-owned tables (nullable
    # for now — backfilled below, then locked to NOT NULL).
    for table in BUSINESS_SCOPED_TABLES:
        op.add_column(table, sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=True))
        op.create_index(f'ix_{table}_business_id', table, ['business_id'])

    # --- 5. Seed the one business this install's existing data belongs to,
    # promote the original admin to platform super_admin, and create a new
    # business_admin to own the shop going forward.
    op.execute(
        f"""
        INSERT INTO businesses (business_id, name, email, phone, created_at, updated_at, is_deleted)
        VALUES ('{BUSINESS_ID}', 'Default Shop', 'shop@hexakomb.com', NULL, now(), now(), false)
        """
    )
    op.execute(
        f"""
        UPDATE users SET role = 'SUPER_ADMIN', business_id = NULL
        WHERE email = '{ORIGINAL_ADMIN_EMAIL}'
        """
    )
    op.execute(
        f"""
        INSERT INTO users (
            user_id, name, email, phone, password_hash, role, business_id,
            created_at, updated_at, is_deleted
        )
        VALUES (
            '{OWNER_USER_ID}', 'Shop Owner', 'owner@hexakomb.com', NULL,
            '{OWNER_PASSWORD_HASH}', 'BUSINESS_ADMIN', '{BUSINESS_ID}', now(), now(), false
        )
        """
    )
    op.execute(f"UPDATE users SET business_id = '{BUSINESS_ID}' WHERE role = 'STAFF'")
    for table in BUSINESS_SCOPED_TABLES:
        op.execute(f"UPDATE {table} SET business_id = '{BUSINESS_ID}'")

    # --- 6. Now that every row has a business_id, lock the columns down.
    for table in BUSINESS_SCOPED_TABLES:
        op.alter_column(table, 'business_id', nullable=False)

    # --- 7. Uniqueness moves from global to per-business.
    op.drop_index('ix_customers_contact', table_name='customers')
    op.create_index('ix_customers_contact', 'customers', ['contact'])
    op.create_unique_constraint(
        'uq_customers_business_contact', 'customers', ['business_id', 'contact']
    )

    op.drop_constraint('items_category_item_name_key', 'items_category', type_='unique')
    op.create_unique_constraint(
        'uq_items_category_business_item_name', 'items_category', ['business_id', 'item_name']
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint('uq_items_category_business_item_name', 'items_category', type_='unique')
    op.create_unique_constraint('items_category_item_name_key', 'items_category', ['item_name'])

    op.drop_constraint('uq_customers_business_contact', 'customers', type_='unique')
    op.drop_index('ix_customers_contact', table_name='customers')
    op.create_index('ix_customers_contact', 'customers', ['contact'], unique=True)

    for table in BUSINESS_SCOPED_TABLES:
        op.drop_index(f'ix_{table}_business_id', table_name=table)
        op.drop_column(table, 'business_id')

    op.drop_constraint('users_business_id_fkey', 'users', type_='foreignkey')
    op.drop_index('ix_users_business_id', table_name='users')
    op.drop_column('users', 'business_id')

    op.drop_index('ix_businesses_email', table_name='businesses')
    op.drop_index('ix_businesses_business_id', table_name='businesses')
    op.drop_table('businesses')

    # Note: the SUPER_ADMIN/BUSINESS_ADMIN enum labels and the seeded/backfilled
    # data are intentionally NOT reverted — Postgres can't drop enum labels,
    # and by the time anyone downgrades, real accounts likely depend on them.
