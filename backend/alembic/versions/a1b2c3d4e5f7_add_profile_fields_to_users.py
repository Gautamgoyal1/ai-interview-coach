"""add profile fields to users

Revision ID: a1b2c3d4e5f7
Revises: f7a8b9c0d1e2
Create Date: 2026-11-13 23:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f7'
down_revision: Union[str, None] = 'f7a8b9c0d1e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('users')]
    if 'target_role' not in columns:
        op.add_column('users', sa.Column('target_role', sa.String(length=120), nullable=True))
    if 'experience_level' not in columns:
        op.add_column('users', sa.Column('experience_level', sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'experience_level')
    op.drop_column('users', 'target_role')
