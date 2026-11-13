"""Add resume analysis deduplication and soft-delete columns.

Revision ID: c4d9e8f1a203
Revises: b7e2f4a19c02
Create Date: 2026-11-12 20:50:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "c4d9e8f1a203"
down_revision = "b7e2f4a19c02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("resume_analyses", sa.Column("user_id", sa.Integer(), nullable=True))
    op.add_column("resume_analyses", sa.Column("resume_hash", sa.String(length=64), nullable=True))
    op.add_column("resume_analyses", sa.Column("analysis_fingerprint", sa.String(length=64), nullable=True))
    op.add_column(
        "resume_analyses",
        sa.Column("status", sa.String(length=24), nullable=False, server_default="completed"),
    )
    op.add_column(
        "resume_analyses",
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column("resume_analyses", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))

    # Backfill user_id and unique legacy hashes for existing rows without losing data.
    op.execute(
        """
        UPDATE resume_analyses ra
        SET user_id = r.user_id,
            resume_hash = COALESCE(ra.resume_hash, 'legacy-resume-' || ra.id::text),
            analysis_fingerprint = COALESCE(ra.analysis_fingerprint, 'legacy-fp-' || ra.id::text)
        FROM resumes r
        WHERE ra.resume_id = r.id
        """
    )

    op.alter_column("resume_analyses", "user_id", nullable=False)
    op.alter_column("resume_analyses", "resume_hash", nullable=False)
    op.alter_column("resume_analyses", "analysis_fingerprint", nullable=False)

    op.create_foreign_key(
        "fk_resume_analyses_user_id_users",
        "resume_analyses",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_resume_analyses_user_id", "resume_analyses", ["user_id"])
    op.create_index("ix_resume_analyses_resume_hash", "resume_analyses", ["resume_hash"])
    op.create_index("ix_resume_analyses_analysis_fingerprint", "resume_analyses", ["analysis_fingerprint"])
    op.create_index("ix_resume_analyses_deleted_at", "resume_analyses", ["deleted_at"])
    op.create_index(
        "uq_resume_analyses_active_fingerprint",
        "resume_analyses",
        ["user_id", "analysis_fingerprint"],
        unique=True,
        postgresql_where=sa.text(
            "deleted_at IS NULL AND status IN ('processing', 'completed')"
        ),
    )


def downgrade() -> None:
    op.drop_index("uq_resume_analyses_active_fingerprint", table_name="resume_analyses")
    op.drop_index("ix_resume_analyses_deleted_at", table_name="resume_analyses")
    op.drop_index("ix_resume_analyses_analysis_fingerprint", table_name="resume_analyses")
    op.drop_index("ix_resume_analyses_resume_hash", table_name="resume_analyses")
    op.drop_index("ix_resume_analyses_user_id", table_name="resume_analyses")
    op.drop_constraint("fk_resume_analyses_user_id_users", "resume_analyses", type_="foreignkey")

    op.drop_column("resume_analyses", "deleted_at")
    op.drop_column("resume_analyses", "version")
    op.drop_column("resume_analyses", "status")
    op.drop_column("resume_analyses", "analysis_fingerprint")
    op.drop_column("resume_analyses", "resume_hash")
    op.drop_column("resume_analyses", "user_id")
