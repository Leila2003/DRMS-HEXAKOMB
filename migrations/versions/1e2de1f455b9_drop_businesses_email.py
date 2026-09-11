"""drop businesses.email

The business itself no longer carries its own email — only the owning
business_admin's user account has one, which is what's used to log in
and to contact them. This drops the now-unused `email` column (and its
unique index) from `businesses`, matching the model/schema changes.

Revision ID: 1e2de1f455b9
Revises: c1e038d21aaf
Create Date: 2026-08-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e2de1f455b9'
down_revision: Union[str, Sequence[str], None] = 'c1e038d21aaf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index('ix_businesses_email', table_name='businesses')
    op.drop_column('businesses', 'email')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('businesses', sa.Column('email', sa.String(length=255), nullable=True))
    op.create_index('ix_businesses_email', 'businesses', ['email'], unique=True)
    # Note: values aren't restored — the column was dropped, not just hidden.
