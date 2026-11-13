"""create interview sessions and turns tables

Revision ID: 9a4c2e1b8f01
Revises: 3fd1df1c2c13
Create Date: 2026-11-12 17:48:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "9a4c2e1b8f01"
down_revision = "3fd1df1c2c13"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "interview_sessions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("resume_analysis_id", sa.Integer(), nullable=False),
        sa.Column("target_role", sa.String(length=150), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("question_index", sa.Integer(), nullable=False),
        sa.Column("max_questions", sa.Integer(), nullable=False),
        sa.Column("follow_up_count", sa.Integer(), nullable=False),
        sa.Column("max_follow_ups", sa.Integer(), nullable=False),
        sa.Column("configuration", sa.JSON(), nullable=False),
        sa.Column("graph_state", sa.JSON(), nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["resume_analysis_id"],
            ["resume_analyses.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_interview_sessions_resume_analysis_id"),
        "interview_sessions",
        ["resume_analysis_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_interview_sessions_user_id"),
        "interview_sessions",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "interview_turns",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("question_id", sa.String(length=64), nullable=False),
        sa.Column("question_index", sa.Integer(), nullable=False),
        sa.Column("is_follow_up", sa.Boolean(), nullable=False),
        sa.Column("parent_question_id", sa.String(length=64), nullable=True),
        sa.Column("topic", sa.String(length=128), nullable=False),
        sa.Column("difficulty", sa.String(length=32), nullable=False),
        sa.Column("question_type", sa.String(length=64), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("rag_sources", sa.JSON(), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=True),
        sa.Column("evaluation", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["interview_sessions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "session_id",
            "question_id",
            name="uq_interview_turns_session_question",
        ),
    )
    op.create_index(
        op.f("ix_interview_turns_session_id"),
        "interview_turns",
        ["session_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_interview_turns_session_id"),
        table_name="interview_turns",
    )
    op.drop_table("interview_turns")
    op.drop_index(
        op.f("ix_interview_sessions_user_id"),
        table_name="interview_sessions",
    )
    op.drop_index(
        op.f("ix_interview_sessions_resume_analysis_id"),
        table_name="interview_sessions",
    )
    op.drop_table("interview_sessions")
