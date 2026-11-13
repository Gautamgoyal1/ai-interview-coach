"""create interview reports table

Revision ID: b7e2f4a19c02
Revises: 9a4c2e1b8f01
Create Date: 2026-11-12 18:12:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "b7e2f4a19c02"
down_revision = "9a4c2e1b8f01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "interview_reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("target_role", sa.String(length=150), nullable=False),
        sa.Column("overall_score", sa.Float(), nullable=True),
        sa.Column("dimension_scores", sa.JSON(), nullable=False),
        sa.Column("topic_scores", sa.JSON(), nullable=False),
        sa.Column("strengths", sa.JSON(), nullable=False),
        sa.Column("weaknesses", sa.JSON(), nullable=False),
        sa.Column("missing_concepts", sa.JSON(), nullable=False),
        sa.Column("recommendations", sa.JSON(), nullable=False),
        sa.Column("question_feedback", sa.JSON(), nullable=False),
        sa.Column("completion_stats", sa.JSON(), nullable=False),
        sa.Column("evaluation_coverage", sa.JSON(), nullable=False),
        sa.Column("rubric_version", sa.String(length=32), nullable=False),
        sa.Column("rubric_weights", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["interview_sessions.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id"),
    )
    op.create_index(
        op.f("ix_interview_reports_session_id"),
        "interview_reports",
        ["session_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_interview_reports_user_id"),
        "interview_reports",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_interview_reports_user_id"),
        table_name="interview_reports",
    )
    op.drop_index(
        op.f("ix_interview_reports_session_id"),
        table_name="interview_reports",
    )
    op.drop_table("interview_reports")
