"""Add persistent private-staging daily endpoint reservations."""
from alembic import op
import sqlalchemy as sa

revision = "b8c9d0e1f2a3"
down_revision = "a1b2c3d4e5f7"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("staging_ai_usage",
        sa.Column("utc_day", sa.Date(), nullable=False),
        sa.Column("bucket", sa.String(64), nullable=False),
        sa.Column("requests", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("utc_day", "bucket"),
        sa.CheckConstraint("requests >= 0", name="ck_staging_ai_usage_nonnegative"))


def downgrade():
    op.drop_table("staging_ai_usage")
