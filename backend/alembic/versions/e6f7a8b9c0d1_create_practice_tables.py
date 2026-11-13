"""Create practice_sessions, practice_questions, and practice_attempts tables.

Revision ID: e6f7a8b9c0d1
Revises: d5e6f7a8b9c0
Create Date: 2026-11-13 14:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "e6f7a8b9c0d1"
down_revision = "d5e6f7a8b9c0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. practice_sessions
    op.create_table(
        "practice_sessions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "interview_type",
            sa.String(length=32),
            nullable=False,
            server_default="technical",
        ),
        sa.Column(
            "target_role",
            sa.String(length=150),
            nullable=False,
            server_default="Software Engineer",
        ),
        sa.Column("topic", sa.String(length=150), nullable=False),
        sa.Column(
            "source_report_id",
            sa.Integer(),
            sa.ForeignKey("interview_reports.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "experience_level",
            sa.String(length=50),
            nullable=False,
            server_default="fresher",
        ),
        sa.Column("weakness_context", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=32),
            nullable=False,
            server_default="active",
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_practice_sessions_user_id", "practice_sessions", ["user_id"]
    )
    op.create_index(
        "ix_practice_sessions_source_report_id",
        "practice_sessions",
        ["source_report_id"],
    )
    op.create_index(
        "ix_practice_sessions_deleted_at", "practice_sessions", ["deleted_at"]
    )

    # 2. practice_questions
    op.create_table(
        "practice_questions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "session_id",
            sa.String(length=36),
            sa.ForeignKey("practice_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("topic", sa.String(length=150), nullable=False),
        sa.Column(
            "difficulty",
            sa.String(length=32),
            nullable=False,
            server_default="medium",
        ),
        sa.Column(
            "hints",
            sa.JSON(),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("reference_answer", sa.Text(), nullable=False),
        sa.Column("reference_explanation", sa.Text(), nullable=True),
        sa.Column(
            "hints_revealed",
            sa.JSON(),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "reference_revealed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "reference_revealed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_practice_questions_session_id", "practice_questions", ["session_id"]
    )

    # 3. practice_attempts
    op.create_table(
        "practice_attempts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "question_id",
            sa.String(length=36),
            sa.ForeignKey("practice_questions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "attempt_number",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
        sa.Column("answer_text", sa.Text(), nullable=False),
        sa.Column(
            "assistance_level",
            sa.String(length=32),
            nullable=False,
            server_default="independent",
        ),
        sa.Column(
            "hints_used",
            sa.JSON(),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "reference_revealed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "feedback",
            sa.JSON(),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "question_id",
            "attempt_number",
            name="uq_practice_attempts_question_attempt",
        ),
    )
    op.create_index(
        "ix_practice_attempts_question_id", "practice_attempts", ["question_id"]
    )
    op.create_index(
        "ix_practice_attempts_user_id", "practice_attempts", ["user_id"]
    )


def downgrade() -> None:
    op.drop_table("practice_attempts")
    op.drop_table("practice_questions")
    op.drop_table("practice_sessions")
