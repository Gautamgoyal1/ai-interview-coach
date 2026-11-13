"""Add interview_type to interview_sessions and interview_reports.

Revision ID: d5e6f7a8b9c0
Revises: c4d9e8f1a203
Create Date: 2026-11-13 13:46:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "d5e6f7a8b9c0"
down_revision = "c4d9e8f1a203"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "interview_sessions",
        sa.Column(
            "interview_type",
            sa.String(length=32),
            nullable=False,
            server_default="technical",
        ),
    )
    op.add_column(
        "interview_reports",
        sa.Column(
            "interview_type",
            sa.String(length=32),
            nullable=False,
            server_default="technical",
        ),
    )


def downgrade() -> None:
    op.drop_column("interview_reports", "interview_type")
    op.drop_column("interview_sessions", "interview_type")
